import os
import json
import numpy as np
from pymongo import MongoClient
from scipy.special import sph_harm
import trimesh  
from descripteurs import voxelize, compute_fourier_coefficients, extract_significant_coefficients, compute_zernike_moments

# Fonction pour réduire le maillage
def reduce_mesh(vertices, faces, reduction_ratio=0.5):
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    if mesh.is_empty:
        print("Le maillage est vide, impossible de réduire.")
        return vertices, faces
    # Utilisation de la méthode decimate pour simplifier le maillage
    simplified_mesh = mesh.simplify_quadratic_decimation(int(len(mesh.faces) * reduction_ratio))
    return simplified_mesh.vertices, simplified_mesh.faces

class OBJDecoder:
    def __init__(self):
        self.data = {
            "vertices": [],
            "normals": [],
            "textures": [],
            "faces": [],
            "groups": []
        }

    def parse(self, filepath):
        self.data = {key: [] for key in self.data}
        with open(filepath, 'r') as file:
            for line in file:
                if line.startswith('#') or not line.strip():
                    continue
                parts = line.split()
                if parts[0] == 'v':
                    self.data["vertices"].append(list(map(float, parts[1:4])))
                elif parts[0] == 'f':
                    face = [int(idx.split('/')[0]) - 1 for idx in parts[1:]]
                    self.data["faces"].append(face)

    def save(self, output_filepath):
        with open(output_filepath, 'w') as file:
            json.dump(self.data, file, indent=4)

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

    # Normalisation des descripteurs
    query_fourier = normalize_descriptor(query_fourier)
    database_fourier = normalize_descriptor(database_fourier)
    query_zernike = normalize_descriptor(query_zernike)
    database_zernike = normalize_descriptor(database_zernike)

    fourier_distance = np.linalg.norm(query_fourier - database_fourier)
    zernike_distance = np.linalg.norm(query_zernike - database_zernike)

    return fourier_distance + zernike_distance

def process_query_model(input_filepath, collection, resolution=64, size=10, l_max=10, target_size=150000, reduction_ratio=0.5):
    decoder = OBJDecoder()
    decoder.parse(input_filepath)
    if not decoder.data["vertices"]:
        print("Aucun sommet détecté.")
        return

    # Réduction du maillage
    vertices = np.array(decoder.data["vertices"])
    faces = np.array(decoder.data["faces"])
    if faces.size > 0:  # Vérifie si le modèle a des faces
        vertices, faces = reduce_mesh(vertices, faces, reduction_ratio)
    else:
        print("Pas de faces dans le modèle, réduction ignorée.")

    grid = voxelize(vertices, resolution)
    fft_coefficients = compute_fourier_coefficients(grid)
    significant_coefficients = extract_significant_coefficients(fft_coefficients, size)
    zernike_moments = compute_zernike_moments(grid, l_max)

    # Normalisation des descripteurs pour le modèle de requête
    significant_coefficients = normalize_descriptor(significant_coefficients)
    zernike_moments = normalize_descriptor(zernike_moments)

    query = {
        "model_name": os.path.basename(input_filepath),
        "fourier_coefficients": significant_coefficients,
        "zernike_moments": zernike_moments
    }

    similarities = []
    for model in collection.find():
        score = calculate_similarity(query, model, target_size)
        similarities.append((model["model_name"], score))

    similarities.sort(key=lambda x: x[1])
    print("Modèles les plus similaires :")
    for model_name, score in similarities[:5]:
        print(f"{model_name}: {score}")

if __name__ == "__main__":
    client = MongoClient("localhost", 27017)
    database_name = "models_databaseRM"
    collection_name = "model_descriptorsRM"
    db = client[database_name]
    collection = db[collection_name]

    input_file = "./3D Models/Alabastron/Alabastron2.obj"
    process_query_model(input_file, collection)
