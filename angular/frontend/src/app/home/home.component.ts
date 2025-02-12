import { Component } from '@angular/core';
import { HttpClientModule, HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';


@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, HttpClientModule],
  templateUrl: './home.component.html',
  styleUrl: './home.component.css',
})
export class HomeComponent {
  uploadedFileName: string | null = null;
  selectedFile: File | null = null;
  isLoading = false;

  searchResults: {
    modelName: string;
    similarityScore: number;
    imageBase64: string;
  }[] = [];

  constructor(private http: HttpClient) {}

  // Gérer la sélection du fichier
  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      const file = input.files[0];
      this.selectedFile = file;
      this.uploadedFileName = file.name;
    }
  }

  /////////////////////////////////
  modifyFile(): void {
    this.selectedFile = null;
    this.uploadedFileName = null;
    this.searchResults = []; // Réinitialiser les résultats de recherche
    const inputElement = document.getElementById('upload') as HTMLInputElement;
    inputElement.value = ''; // Réinitialiser l'input
  }
  // 7it mtstorawch f mongo b prefixe
  getImageWithPrefix(base64String: string): string {
    if (base64String.startsWith('/9j/')) {
      return `data:image/jpeg;base64,${base64String}`;
    } else if (base64String.startsWith('iVBOR')) {
      return `data:image/png;base64,${base64String}`;
    } else if (base64String.startsWith('PHN2ZyB4')) {
      return `data:image/svg+xml;base64,${base64String}`;
    } else if (base64String.startsWith('AAAA')) {
      return `data:image/webp;base64,${base64String}`;
    }
    return ''; //nn valide
  }

  isImage(base64String: string): boolean {
    return (
      base64String.startsWith('/9j/') ||
      base64String.startsWith('iVBOR') ||
      base64String.startsWith('PHN2ZyB4') ||
      base64String.startsWith('AAAA')
    );
  }

  startSearch() {
    this.isLoading = true;

    // Simuler une recherche (remplacez par votre logique réelle)
    setTimeout(() => {
      this.isLoading = false;
      this.searchResults = [];
    }, 3000);
  }

  // Envoyer le fichier au serveur
  uploadFile(): void {
    if (this.selectedFile) {
      this.isLoading = true;

      const formData = new FormData();
      formData.append('file', this.selectedFile);

      this.http.post<any>('http://localhost:3000/upload', formData).subscribe(
        (response) => {
          this.searchResults = response.similarities.map((item: any) => ({
            modelName: item.model_name,
            similarityScore: item.similarity_score,
            imageBase64: item.image_base64,
          }));
          this.isLoading = false;
        },
        (error) => {
          console.error("Erreur lors de l'upload du fichier", error);
          this.searchResults = [];
          this.isLoading = false;
        }
      );
    }
  }
}
