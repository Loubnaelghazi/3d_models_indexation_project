import os
import json
import numpy as np
from pymongo import MongoClient
from scipy.special import sph_harm

# Fonction pour convertir des sommets en grille voxelisée
def voxelize(vertices, resolution=64):
    vertices = np.array(vertices)
    vertices -= np.min(vertices, axis=0)
    vertices /= np.ptp(vertices, axis=0)  # Utilisation de ptp pour éviter division par zéro
    grid = np.zeros((resolution, resolution, resolution))
    for v in vertices:
        x, y, z = np.clip((v * (resolution - 1)).astype(int), 0, resolution - 1)
        grid[x, y, z] = 1
    return grid

# Calcul des coefficients de Fourier
def compute_fourier_coefficients(grid):
    fft_result = np.fft.fftn(grid)
    fft_shifted = np.fft.fftshift(fft_result)
    return np.abs(fft_shifted)

# Extraction des coefficients significatifs
def extract_significant_coefficients(fft_coefficients, size=10):
    center = np.array(fft_coefficients.shape) // 2
    low_freq_region = fft_coefficients[
        max(center[0]-size, 0):center[0]+size,
        max(center[1]-size, 0):center[1]+size,
        max(center[2]-size, 0):center[2]+size
    ]
    return low_freq_region.flatten()

# Normalisation des descripteurs
def normalize_descriptor(descriptor):
    norm = np.linalg.norm(descriptor)
    if norm == 0:
        return descriptor
    return descriptor / norm

# Conversion cartésien -> sphérique
def cartesian_to_spherical(x, y, z):
    r = np.sqrt(x**2 + y**2 + z**2)
    theta = np.arccos(z / r) if r != 0 else 0
    phi = np.arctan2(y, x)
    return r, theta, phi

# Calcul des moments de Zernike
def compute_zernike_moments(grid, l_max=10):
    size = grid.shape[0]
    center = size // 2
    moments = []
    for x in range(size):
        for y in range(size):
            for z in range(size):
                if grid[x, y, z] > 0:
                    r, theta, phi = cartesian_to_spherical(
                        x - center, y - center, z - center
                    )
                    for l in range(l_max + 1):
                        for m in range(-l, l + 1):
                            Y_lm = sph_harm(m, l, phi, theta)
                            moments.append((r**l) * np.real(Y_lm))
    return np.array(moments)

# Traitement et stockage dans MongoDB
def process_json_file(json_filepath, collection, resolution=64, size=10, l_max=10):
    with open(json_filepath, 'r') as file:
        data = json.load(file)

    vertices = data.get("vertices", [])
    if not vertices:
        print(f"Aucun sommet trouvé dans {json_filepath}, fichier ignoré.")
        return

    grid = voxelize(vertices, resolution)
    fft_coefficients = compute_fourier_coefficients(grid)
    significant_coefficients = extract_significant_coefficients(fft_coefficients, size)
    zernike_moments = compute_zernike_moments(grid, l_max)

    # Normalisation des descripteurs
    normalized_fourier = normalize_descriptor(significant_coefficients)
    normalized_zernike = normalize_descriptor(zernike_moments)

    document = {
        "model_name": os.path.basename(json_filepath),
        "fourier_coefficients": normalized_fourier.tolist(),
        "zernike_moments": normalized_zernike.tolist()
    }

    collection.insert_one(document)
    print(f"Descripteurs sauvegardés pour : {os.path.basename(json_filepath)}")

if __name__ == "__main__":
    client = MongoClient("localhost", 27017)
    database_name = "models_database"
    collection_name = "model_descriptors"
    db = client[database_name]
    collection = db[collection_name]

    input_directory = "./decodage"

    for root, dirs, files in os.walk(input_directory):
        for filename in files:
            if filename.endswith('.json'):
                json_filepath = os.path.join(root, filename)
                try:
                    process_json_file(json_filepath, collection, resolution=64, size=10, l_max=10)
                except Exception as e:
                    print(f"Erreur lors du traitement de {filename} : {e}")

    print("Traitement terminé.")
