import os
import json

class OBJDecoder:
    def __init__(self):
        self.data = {
            "vertices": [],
            "normals": [],
            "textures": [],
            "faces": [],
            "groups": []
        }
        self.current_group = None

    def parse(self, filepath):
        self.data = {
            "vertices": [],
            "normals": [],
            "textures": [],
            "faces": [],
            "groups": []
        }
        self.current_group = None

        print(f"Reading file: {filepath}")
        with open(filepath, 'r') as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split()
                keyword = parts[0]
                if keyword == 'v':
                    x, y, z = map(float, parts[1:4])
                    self.data["vertices"].append([x, y, z])
                elif keyword == 'vn':
                    dx, dy, dz = map(float, parts[1:4])
                    self.data["normals"].append([dx, dy, dz])
                elif keyword == 'vt':
                    u, v = map(float, parts[1:3])
                    self.data["textures"].append([u, v])
                elif keyword == 'f':
                    face_data = []
                    for vertex in parts[1:]:
                        indices = vertex.split('/')
                        vertex_index = int(indices[0]) - 1
                        texture_index = int(indices[1]) - 1 if len(indices) > 1 and indices[1] else None
                        normal_index = int(indices[2]) - 1 if len(indices) > 2 and indices[2] else None
                        face_data.append({
                            "vertex": vertex_index,
                            "texture": texture_index,
                            "normal": normal_index
                        })
                    self.data["faces"].append({
                        "group": self.current_group,
                        "vertices": face_data
                    })
                elif keyword == 'g':
                    self.current_group = parts[1]
                    if self.current_group not in self.data["groups"]:
                        self.data["groups"].append(self.current_group)

    def save(self, output_filepath):
        with open(output_filepath, 'w') as file:
            json.dump(self.data, file, indent=4)
        print(f"Results saved to {output_filepath}")



if __name__ == "__main__":
    input_directory = "./3D Models"  #  dossier source
    output_directory = "./decodage"  #  dossier cible

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        print(f"Output directory created: {output_directory}")

    decoder = OBJDecoder()
    files_processed = 0

    for root, dirs, files in os.walk(input_directory):
        for filename in files:
            if filename.endswith('.obj'):
                # Chemin complet vers le fichier d'entrée
                input_filepath = os.path.join(root, filename)

                # Nom de sortie basé uniquement sur le nom du fichier .obj
                output_filename = f"{os.path.splitext(filename)[0]}.json"
                output_filepath = os.path.join(output_directory, output_filename)

                print(f"Processing: {input_filepath}")
                try:
                    decoder.parse(input_filepath)
                    print(f"Parsed {len(decoder.data['vertices'])} vertices and {len(decoder.data['faces'])} faces.")
                    if decoder.data["vertices"] or decoder.data["faces"]:
                        decoder.save(output_filepath)
                        files_processed += 1
                    else:
                        print(f"No valid data found in {filename}, skipping.")
                except Exception as e:
                    print(f"Error processing {filename}: {e}")

    if files_processed > 0:
        print(f"Processing complete. {files_processed} files saved in the output folder.")
    else:
        print("No valid .obj files were processed.")
