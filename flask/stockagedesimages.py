import os
import base64
from pymongo import MongoClient

def encode_image_to_base64(image_path):
    """
    Convertit une image en chaîne base64.
    """
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string

def process_image_directory(image_directory, collection):
    """
    Parcourt un dossier contenant des sous-dossiers d'images et les associe aux entrées MongoDB existantes.
    Ignore les différences entre majuscules et minuscules.
    """
    for root, dirs, files in os.walk(image_directory):  # Parcourt récursivement le dossier
        for filename in files:
            if filename.endswith('.jpg'):  # Filtre les fichiers .jpg
                # Obtenir le chemin complet de l'image
                image_path = os.path.join(root, filename)
                
                # Obtenir le nom du modèle (nom du fichier sans extension) et ajouter l'extension ".json"
                model_name = f"{filename.replace('.jpg', '').lower()}.json"  # Normalisation en minuscules

                # Convertir l'image en base64
                image_base64 = encode_image_to_base64(image_path)

                # Rechercher dans la collection de manière insensible à la casse
                result = collection.update_one(
                    {"model_name": {"$regex": f"^{model_name}$", "$options": "i"}},  # Recherche insensible à la casse
                    {"$set": {"image_base64": image_base64}}  # Ajoute ou met à jour le champ image_base64
                )

                # Message pour suivre les mises à jour
                if result.matched_count > 0:
                    print(f"Image ajoutée pour le modèle : {model_name}")
                else:
                    print(f"Aucun modèle trouvé pour l'image : {filename}")

if __name__ == "__main__":
    client = MongoClient("localhost", 27017)
    database_name = "models_databaseRM"       #models_databse
    collection_name = "model_descriptorsRM"   # or model_descriptors
    db = client[database_name]
    collection = db[collection_name]

    # Dossier contenant les sous-dossiers avec les images
    image_directory = "./Thumbnails"

    process_image_directory(image_directory, collection)

    print("Traitement des images terminé.")
