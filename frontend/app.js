document.addEventListener("DOMContentLoaded", () => {
  // === Sélecteurs DOM ===
  const form = document.getElementById("predictForm");
  const diplomasContainer = document.getElementById("diplomasContainer");
  const experiencesContainer = document.getElementById("experiencesContainer");
  const pastCoursesContainer = document.getElementById("pastCoursesContainer");
  const addDiplomaBtn = document.getElementById("addDiplomaBtn");
  const addExperienceBtn = document.getElementById("addExperienceBtn");
  const addPastCourseBtn = document.getElementById("addPastCourseBtn");
  const generateBtn = document.getElementById("generateBtn");
  const resetBtn = document.getElementById("resetBtn");
  const loader = document.getElementById("loader");
  const result = document.getElementById("result");

  // === Données de base ===
  const subjects = {
    informatique: {
      desc: "Formateur expérimenté en développement web, IA et programmation.",
      diplomas: [
        ["Licence en Informatique", "Licence"],
        ["Master en Informatique", "Master"],
        ["Doctorat en Informatique", "Doctorat"]
      ],
      experiences: [
        "Développeur Full Stack",
        "Formateur Web",
        "Professeur d'Informatique",
        "Chercheur en IA"
      ],
      companies: ["École 42", "Université de Lyon", "CNRS", "EPITA"],
      courses: [
        "Programmation Python",
        "Développement Web avec React",
        "Algorithmes et Structures de Données",
        "Intelligence Artificielle"
      ]
    },
    maths: {
      desc: "Enseignant en mathématiques appliquées et statistiques.",
      diplomas: [
        ["Licence en Mathématiques", "Licence"],
        ["Master en Mathématiques Appliquées", "Master"],
        ["Doctorat en Mathématiques", "Doctorat"]
      ],
      experiences: [
        "Professeur de Mathématiques",
        "Chercheur en Statistiques",
        "Data Scientist"
      ],
      companies: ["Université de Paris", "INRIA", "CNRS"],
      courses: [
        "Analyse Mathématique",
        "Algèbre Linéaire",
        "Statistiques",
        "Probabilités"
      ]
    },
    français: {
      desc: "Professeur de littérature et linguistique française.",
      diplomas: [
        ["Licence Lettres Modernes", "Licence"],
        ["Master en Linguistique", "Master"],
        ["Doctorat en Littérature Comparée", "Doctorat"]
      ],
      experiences: [
        "Professeur de Français",
        "Chercheur en Linguistique",
        "Rédacteur"
      ],
      companies: ["Sorbonne Université", "Université de Lyon", "Université de Bordeaux"],
      courses: [
        "Grammaire Avancée",
        "Analyse de Texte Littéraire",
        "Poésie et Rhétorique",
        "Expression Orale"
      ]
    },
    physique: {
      desc: "Professeur spécialisé en physique appliquée et mécanique.",
      diplomas: [
        ["Licence en Physique", "Licence"],
        ["Master en Physique Appliquée", "Master"],
        ["Doctorat en Énergie et Thermodynamique", "Doctorat"]
      ],
      experiences: [
        "Professeur de Physique",
        "Chercheur en Énergie",
        "Ingénieur en Mécanique"
      ],
      companies: ["CEA Grenoble", "Université Grenoble Alpes", "CNRS"],
      courses: [
        "Mécanique des Fluides",
        "Thermodynamique",
        "Physique Quantique",
        "Électricité et Magnétisme"
      ]
    },
    chimie: {
      desc: "Professeur en chimie organique et science des matériaux.",
      diplomas: [
        ["Licence en Chimie", "Licence"],
        ["Master en Chimie Organique", "Master"],
        ["Doctorat en Sciences des Matériaux", "Doctorat"]
      ],
      experiences: [
        "Professeur de Chimie",
        "Chercheur en Matériaux",
        "Formateur en Laboratoire"
      ],
      companies: ["Université de Lille", "CNRS", "Université de Lyon"],
      courses: [
        "Chimie Organique",
        "Chimie des Matériaux",
        "Spectroscopie Avancée",
        "Thermochimie"
      ]
    },
    histoire: {
      desc: "Historien spécialiste de la Révolution française.",
      diplomas: [
        ["Licence en Histoire", "Licence"],
        ["Master en Histoire Moderne", "Master"],
        ["Doctorat en Civilisations Européennes", "Doctorat"]
      ],
      experiences: [
        "Professeur d'Histoire",
        "Chercheur en Histoire Moderne",
        "Archiviste"
      ],
      companies: ["Université de Paris", "Université de Bordeaux", "CNRS"],
      courses: [
        "Révolution Française",
        "Civilisations Anciennes",
        "Guerres Mondiales",
        "Histoire Contemporaine"
      ]
    }
  };

  // === Utilitaires ===
  const getRandom = (arr) => arr[Math.floor(Math.random() * arr.length)];

  function clearAllFields() {
    document.getElementById("fistname").value = "";
    document.getElementById("lastname").value = "";
    document.getElementById("city").value = "";
    document.getElementById("description").value = "";
    document.getElementById("courseTitle").value = "";
    document.getElementById("courseDesc").value = "";
    diplomasContainer.innerHTML = "";
    experiencesContainer.innerHTML = "";
    pastCoursesContainer.innerHTML = "";
    result.style.display = "none";
  }

  // === Création d’éléments dynamiques ===
  const createDiploma = (title, level) => {
    const div = document.createElement("div");
    div.className = "entry";
    div.innerHTML = `
      <label>Titre</label>
      <input type="text" class="diplomaTitle" value="${title}">
      <label>Niveau</label>
      <input type="text" class="diplomaLevel" value="${level}">
    `;
    diplomasContainer.appendChild(div);
  };

  const createExperience = (title, company) => {
    const div = document.createElement("div");
    div.className = "entry";
    div.innerHTML = `
      <label>Titre du poste</label>
      <input type="text" class="expTitle" value="${title}">
      <label>Entreprise</label>
      <input type="text" class="expCompany" value="${company}">
      <label>Description</label>
      <textarea class="expDesc" rows="2">Expérience professionnelle en ${title.toLowerCase()}.</textarea>
      <label>Durée</label>
      <input type="text" class="expDuration" value="3 ans">
    `;
    experiencesContainer.appendChild(div);
  };

  const createPastCourse = (title, stars) => {
    const div = document.createElement("div");
    div.className = "entry";
    div.innerHTML = `
      <label>Titre du cours</label>
      <input type="text" class="pastCourseTitle" value="${title}">
      <label>Description</label>
      <textarea class="pastCourseDesc" rows="2">Cours sur ${title.toLowerCase()}.</textarea>
      <label>Note moyenne</label>
      <input type="number" class="pastCourseStars" min="1" max="5" step="0.1" value="${stars}">
    `;
    pastCoursesContainer.appendChild(div);
  };

  // === Génération automatique complète ===
  function generateFullProfile() {
    clearAllFields();

    const domainKeys = Object.keys(subjects);
    const domain = getRandom(domainKeys);
    const data = subjects[domain];

    // Profil général
    document.getElementById("fistname").value = getRandom(["Jean", "Claire", "Luc", "Marie", "Antoine"]);
    document.getElementById("lastname").value = getRandom(["Martin", "Dubois", "Durand", "Lemoine", "Petit"]);
    document.getElementById("city").value = getRandom(["Paris", "Lyon", "Marseille", "Toulouse"]);
    document.getElementById("description").value = data.desc;

    // Diplômes
    const nbDiplomas = Math.floor(Math.random() * 2) + 1;
    for (let i = 0; i < nbDiplomas; i++) {
      const [title, level] = getRandom(data.diplomas);
      createDiploma(title, level);
    }

    // Expériences
    const nbExp = Math.floor(Math.random() * 2) + 1;
    for (let i = 0; i < nbExp; i++) {
      createExperience(getRandom(data.experiences), getRandom(data.companies));
    }

    // Cours passés
    const nbPast = Math.floor(Math.random() * 2) + 1;
    for (let i = 0; i < nbPast; i++) {
      createPastCourse(getRandom(data.courses), (3.5 + Math.random() * 1.5).toFixed(1));
    }

    // Cours à venir (corrélé ou non)
    const correlated = Math.random() < 0.5;
    const courseDomain = correlated ? domain : getRandom(domainKeys.filter(d => d !== domain));
    const courseData = subjects[courseDomain];
    const courseTitle = getRandom(courseData.courses);
    document.getElementById("courseTitle").value = courseTitle;
    document.getElementById("courseDesc").value = `Cours approfondi sur ${courseTitle.toLowerCase()}.`;

    alert(`✅ Professeur généré (${domain})\n📖 Cours à venir : ${courseTitle} (${correlated ? "corrélé" : "non corrélé"})`);
  }

  // === Réinitialiser ===
  resetBtn.addEventListener("click", clearAllFields);

  // === Générer un profil complet ===
  generateBtn.addEventListener("click", generateFullProfile);

  // === Ajouts manuels ===
  addDiplomaBtn.addEventListener("click", () => createDiploma("", ""));
  addExperienceBtn.addEventListener("click", () => createExperience("", ""));
  addPastCourseBtn.addEventListener("click", () => createPastCourse("", 4.5));

  // === Soumission du formulaire ===
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    loader.style.display = "block";
    result.style.display = "none";

    const diplomas = Array.from(diplomasContainer.querySelectorAll(".entry")).map(d => ({
      level: d.querySelector(".diplomaLevel").value,
      title: d.querySelector(".diplomaTitle").value
    }));

    const experiences = Array.from(experiencesContainer.querySelectorAll(".entry")).map(e => ({
      company: e.querySelector(".expCompany").value,
      title: e.querySelector(".expTitle").value,
      description: e.querySelector(".expDesc").value,
      duration: e.querySelector(".expDuration").value
    }));

    const pastCourses = Array.from(pastCoursesContainer.querySelectorAll(".entry")).map(c => ({
      title: c.querySelector(".pastCourseTitle").value,
      description: c.querySelector(".pastCourseDesc").value,
      numberOfStars: parseFloat(c.querySelector(".pastCourseStars").value)
    }));

    const professor = {
      fistname: document.getElementById("fistname").value,
      lastname: document.getElementById("lastname").value,
      city: document.getElementById("city").value,
      description: document.getElementById("description").value,
      diplomas,
      experiences,
      pastCourses
    };

    const course = {
      title: document.getElementById("courseTitle").value,
      description: document.getElementById("courseDesc").value
    };

    const payload = { professor, course };

    try {
      console.log("📦 Données envoyées à l’API :", JSON.stringify(payload, null, 2));

      const response = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const data = await response.json();
      loader.style.display = "none";

      if (!response.ok) {
        result.innerHTML = "❌ Erreur API : " + (data.detail || "inconnue");
      } else {
        const score = parseFloat(data.gradeAverage);
        let color = score < 2.5 ? "#ff5c5c" : score < 4 ? "#ffcc00" : "#00ffcc";
        result.innerHTML = `⭐ Note prédite : <span style="color:${color}">${score.toFixed(2)}</span> / 5`;
      }
    } catch (err) {
      loader.style.display = "none";
      result.innerHTML = "❌ Erreur réseau : " + err.message;
    }

    result.style.display = "block";
  });
});
