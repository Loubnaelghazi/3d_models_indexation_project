#  3D Model Retrieval and Indexing System  

##  Table of Contents  
1. [Project Overview](#project-overview)  
2. [Features](#features)  
3. [Tech Stack](#tech-stack)  
4. [Architecture](#architecture)  
5. [Project Structure](#project-structure)  
6. [Installation & Setup](#installation--setup)  
7. [Usage](#usage)  
8. [Performance Comparison](#performance-comparison)  
9. [Contributors](#contributors)  
10. [Supervision](#supervision)  
11. [License](#license)  

##  Project Overview  
This project is a **content-based retrieval system** for 3D models, leveraging **Fourier descriptors and Zernike moments** to analyze and compare shapes efficiently. The system supports **similarity search** with and without **mesh reduction**, improving performance while maintaining high accuracy.  

##  Features  
- **3D Model Upload & Processing**  
  - Supports `.obj` file format  
  - Extracts shape descriptors using **Fourier Transform** & **Zernike Moments**  
- **Content-Based Search Methods**  
  - **Standard Search:** Compares models based on raw descriptors  
  - **Optimized Search:** Uses **mesh reduction** for improved efficiency  
- **Performance Optimization**  
  - **30% faster** with **quadratic decimation**  
  - Maintains similarity accuracy while reducing computation  

##  Tech Stack  
- **Frontend:** Angular  
- **Backend:** Node.js (Express)  
- **Database:** MongoDB  
- **3D Processing:** Flask, Trimesh, Open3D  

##  Architecture  
1️⃣ **Frontend (Angular UI)** - Allows users to upload models, view results, and compare similarity scores.  
2️⃣ **Backend (Node.js & Express)** - Handles API requests and interacts with the database(from Flask).  
3️⃣ **Database (MongoDB)** - Stores extracted descriptors and search results.  
4️⃣ **3D Processing (Flask API)** - Computes Fourier & Zernike descriptors and applies mesh reduction.  

##  Project Structure  
```bash  
 3D-Model-Retrieval  
├── 📂 frontend/ (Angular UI)  
├── 📂 backend/ (Node.js API)  
├── 📂 flask_api/ (Image Processing & Feature Extraction)  
└── 📂 database/ (MongoDB Collections)  
```

##  Installation & Setup  
### 1️⃣ Clone the Repository  
```bash  
git clone https://github.com/Loubnaelghazi/3D-models_indexation_project.git  
cd 3D-models_indexation_project  
```

### 2️⃣ Backend Setup (Node.js)  
```bash  
cd backend  
npm install  
npm start  
```

### 3️⃣ Frontend Setup (Angular)  
```bash  
cd frontend  
npm install  
ng serve  
```

### 4️⃣ Flask API Setup  
```bash  
cd flask_api  
pip install -r requirements.txt  
python api.py  
```

### 5️⃣ Run MongoDB  
Ensure MongoDB is running .  

##  Usage  
1️⃣ **Upload** a `.obj` 3D model via the web UI.  
2️⃣ Choose between **Standard Search** or **Optimized Search (with mesh reduction)**.  
3️⃣ The system will compute shape descriptors and retrieve the **most similar 3D models**.  
4️⃣ Compare results visually and analyze similarity scores.  

##  Performance Comparison  
| Method              | Processing Time | Similarity Accuracy |  
|---------------------|----------------|----------------------|  
| Standard Search    | High            | Very High            |  
| Mesh Reduction     | **30% Faster**  | Slightly Reduced     |  

##  Contributors  
- **Loubna El Ghazi**  
- Widad Essetti  
- Imane Elaoufi  

##  Supervision  
**Prof. M'hamed AIT KBIR**  

##  License  
This project is licensed under the **MIT License**.  

---  
 **Enhancing 3D model search with AI-powered shape analysis!**
