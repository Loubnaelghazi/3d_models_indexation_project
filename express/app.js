const express = require("express");
const axios = require("axios");
const multer = require("multer");
const fs = require("fs");
const path = require("path");
const FormData = require("form-data"); 
const cors = require("cors");
const bodyParser = require("body-parser");

const app = express();
const port = 3000;

const corsOptions = {
  origin: "http://localhost:4200",
  methods: "GET,HEAD,PUT,PATCH,POST,DELETE",
  allowedHeaders: ["Content-Type", "Authorization"],
  credentials: true, 
};
app.use(cors(corsOptions));
app.options("*", cors(corsOptions)); 

app.use(bodyParser.json());
//////////////////////////////////////////////////////////////////////

const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, "uploads/"); 
  },
  filename: (req, file, cb) => {
    cb(null, file.originalname); 
  },
});


const upload = multer({ storage: storage });

/////////////////////////////////////////////////////////////////////////////////
app.post("/upload", upload.single("file"), async (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: "Aucun fichier téléchargé." });
  }

  try {
    const filePath = path.join(__dirname, "uploads", req.file.filename);

    
    const form = new FormData();
    form.append("file", fs.createReadStream(filePath)); 

    // 
    const flaskUrl = "http://localhost:5000/upload";
    const headers = form.getHeaders(); 

    // 
    const response = await axios.post(flaskUrl, form, { headers });

    // 
    res.status(200).json(response.data);
  } catch (error) {
    console.error("Erreur lors de la communication avec Flask:", error.message);
    res
      .status(500)
      .json({ error: "Erreur lors de la communication avec Flask." });
  }
});
//////////////////////////////////////////////////////////////

app.post("/reduce", upload.single("file"), async (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: "Aucun fichier téléchargé." });
  }

  try {
    const filePath = path.join(__dirname, "uploads", req.file.filename);

    const form = new FormData();
    form.append("file", fs.createReadStream(filePath));

    const flaskUrl = "http://localhost:5000/reduce"; 
    const headers = form.getHeaders();

    const response = await axios.post(flaskUrl, form, { headers });

    res.status(200).json(response.data);
  } catch (error) {
    console.error("Erreur lors de la communication avec Flask:", error.message);
    res
      .status(500)
      .json({ error: "Erreur lors de la communication avec Flask." });
  }
});





app.listen(port, () => {
  console.log(
    `Serveur Express en cours d'exécution sur http://localhost:${port}`
  );
});
