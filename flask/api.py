from flask import Flask, request, jsonify
from pymongo import MongoClient
import os
import json
import numpy as np
from descripteurs import voxelize, compute_fourier_coefficients, extract_significant_coefficients, compute_zernike_moments ,cartesian_to_spherical
from querydescriptorsRM import OBJDecoder
from descripteursRM import reduce_mesh 




app = Flask(__name__)
UPLOAD_FOLDER = './uploads'
DECODER_FOLDER = './decodage'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

client = MongoClient("localhost", 27017)
db = client["models_database"]
collection = db["model_descriptors"]
###########

# Connexion MongoDB pour /reduce
client_rm = MongoClient("localhost", 27017)
db_rm = client_rm["models_databaseRM"]
collection_rm = db_rm["model_descriptorsRM"]

def load_decoded_object(filename):
    json_filepath = os.path.join(DECODER_FOLDER, f"{filename}.json")
    if not os.path.exists(json_filepath):
        raise FileNotFoundError(f"Le fichier décodé pour {filename} n'a pas été trouvé.")
    
    with open(json_filepath, 'r') as f:
        decoded_object = json.load(f)
    
    return decoded_object

def adjust_descriptor_size(descriptor, target_size):
    descriptor = np.array(descriptor)
    if len(descriptor) < target_size:
        descriptor = np.pad(descriptor, (0, target_size - len(descriptor)))
    elif len(descriptor) > target_size:
        descriptor = descriptor[:target_size]
    return descriptor

def normalize_descriptor(descriptor):
    norm = np.linalg.norm(descriptor)
    if norm == 0:
        return descriptor
    return descriptor / norm

def calculate_similarity(query, database, target_size):
    query_fourier = adjust_descriptor_size(query["fourier_coefficients"], target_size)
    database_fourier = adjust_descriptor_size(database["fourier_coefficients"], target_size)

    query_zernike = adjust_descriptor_size(query["zernike_moments"], target_size)
    database_zernike = adjust_descriptor_size(database["zernike_moments"], target_size)

    query_fourier = normalize_descriptor(query_fourier)
    database_fourier = normalize_descriptor(database_fourier)
    query_zernike = normalize_descriptor(query_zernike)
    database_zernike = normalize_descriptor(database_zernike)

    fourier_distance = np.linalg.norm(query_fourier - database_fourier)
    zernike_distance = np.linalg.norm(query_zernike - database_zernike)

    return fourier_distance + zernike_distance

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "Aucun fichier téléchargé."}), 400
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "Le nom du fichier est vide."}), 400
    
    try:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        
        decoded_object = load_decoded_object(file.filename.split('.')[0])


        
        grid = voxelize(decoded_object["vertices"], resolution=64)
        fft_coefficients = compute_fourier_coefficients(grid)
        significant_coefficients = extract_significant_coefficients(fft_coefficients, size=10)
        zernike_moments = compute_zernike_moments(grid, l_max=10)

        significant_coefficients = normalize_descriptor(significant_coefficients)
        zernike_moments = normalize_descriptor(zernike_moments)

        query = {
            "model_name": file.filename,
            "fourier_coefficients": significant_coefficients,
            "zernike_moments": zernike_moments
        }
        
        similarities = []
        for model in collection.find():
            score = calculate_similarity(query, model, target_size=150000)
            similarities.append({
                "model_name": model["model_name"],
                "similarity_score": score,
                "image_base64": model.get("image_base64", None)
            })
        
        similarities.sort(key=lambda x: x["similarity_score"])
        
        return jsonify({
            "message": "Traitement terminé.",
            "similarities": similarities[:10],
        })
    
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500




@app.route('/reduce', methods=['POST'])
def upload_and_reduce_file():
    if 'file' not in request.files:
        return jsonify({"error": "Aucun fichier téléchargé."}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "Le nom du fichier est vide."}), 400

    try:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        decoder = OBJDecoder()
        decoder.parse(filepath)
        if not decoder.data["vertices"]:
            return jsonify({"error": "Aucun sommet détecté dans le fichier."}), 400

        # Réduction du maillage
        vertices = np.array(decoder.data["vertices"])
        faces = np.array(decoder.data["faces"])
        if faces.size > 0:  # Vérifie si le modèle contient des faces
            vertices, faces = reduce_mesh(vertices, faces, reduction_ratio=0.6)
        else:
            return jsonify({"error": "Pas de faces dans le modèle. Réduction ignorée."}), 400

        # Calcul des descripteurs
        grid = voxelize(vertices, resolution=64)
        fft_coefficients = compute_fourier_coefficients(grid)
        significant_coefficients = extract_significant_coefficients(fft_coefficients, size=10)
        zernike_moments = compute_zernike_moments(grid, l_max=10)

        significant_coefficients = normalize_descriptor(significant_coefficients)
        zernike_moments = normalize_descriptor(zernike_moments)

        
        query = {
            "model_name": file.filename,
            "fourier_coefficients": significant_coefficients.tolist(),
            "zernike_moments": zernike_moments.tolist()
        }

        
        collection_rm.insert_one(query)
        
        similarities = []
        for model in collection.find():
            score = calculate_similarity(query, model, target_size=150000)
            similarities.append({
                "model_name": model["model_name"],
                "similarity_score": score,
                "image_base64": model.get("image_base64", None)
            })

        
        filtered_similarities = [
            similarity for similarity in similarities
            if similarity["similarity_score"] > 0 and similarity["similarity_score"] is not None
        ]

        
        filtered_similarities.sort(key=lambda x: x["similarity_score"])

        return jsonify({
            "message": "Traitement terminé.",
            "similarities": filtered_similarities[:10], 
        })


    except Exception as e:
        return jsonify({"error": str(e)}), 500








if __name__ == "__main__":
    app.run(debug=True)
