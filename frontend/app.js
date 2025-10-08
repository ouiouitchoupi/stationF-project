document.addEventListener("DOMContentLoaded", () => {
  // ==== Références DOM ====
  const form = document.getElementById('predictForm');
  const diplomasContainer = document.getElementById('diplomasContainer');
  const experiencesContainer = document.getElementById('experiencesContainer');
  const addDiplomaBtn = document.getElementById('addDiplomaBtn');
  const addExperienceBtn = document.getElementById('addExperienceBtn');
  const randomProfileBtn = document.getElementById('randomProfileBtn');
  const loader = document.getElementById('loader');
  const result = document.getElementById('result');

  // ==== Fonctions utilitaires ====
  function createDiplomaEntry(title = "", level = "") {
    const div = document.createElement('div');
    div.className = 'entry';
    div.innerHTML = `
      <button type="button" class="remove-btn">🗑️</button>
      <label>Titre du diplôme</label>
      <select class="diplomaTitle">
        <option>Licence en Informatique</option>
        <option>Master en Informatique</option>
        <option>Doctorat en Informatique</option>
        <option>Licence en Mathématiques</option>
        <option>Master en Mathématiques</option>
        <option>Licence Lettres Modernes</option>
        <option>Master Linguistique</option>
        <option>Master Physique</option>
        <option>Doctorat Chimie</option>
        <option>Doctorat Histoire</option>
      </select>
      <label>Niveau</label>
      <select class="diplomaLevel">
        <option>Certificat</option>
        <option>Licence</option>
        <option>Maîtrise</option>
        <option>Master</option>
        <option>Doctorat</option>
      </select>
    `;
    if (title) div.querySelector('.diplomaTitle').value = title;
    if (level) div.querySelector('.diplomaLevel').value = level;
    div.querySelector('.remove-btn').addEventListener('click', () => div.remove());
    diplomasContainer.appendChild(div);
  }

  function createExperienceEntry(title = "", company = "") {
    const div = document.createElement('div');
    div.className = 'entry';
    div.innerHTML = `
      <button type="button" class="remove-btn">🗑️</button>
      <label>Titre du poste</label>
      <select class="expTitle">
        <option>Professeur</option>
        <option>Formateur</option>
        <option>Chercheur</option>
        <option>Data Scientist</option>
        <option>Chargé de cours</option>
      </select>
      <label>Établissement / Entreprise</label>
      <select class="expCompany">
        <option>École 42</option>
        <option>Sorbonne Université</option>
        <option>Polytechnique</option>
        <option>HEC Paris</option>
        <option>Université de Lyon</option>
        <option>Université de Toulouse</option>
        <option>CNRS</option>
        <option>Autre</option>
      </select>
    `;
    if (title) div.querySelector('.expTitle').value = title;
    if (company) div.querySelector('.expCompany').value = company;
    div.querySelector('.remove-btn').addEventListener('click', () => div.remove());
    experiencesContainer.appendChild(div);
  }

  // ==== Génération de profil aléatoire ====
  function generateRandomProfile() {
    const domains = ["informatique", "maths", "français", "physique", "chimie", "histoire"];
    const descriptions = {
      informatique: "Professeur passionné de programmation et de développement web.",
      maths: "Enseignant en mathématiques appliquées et statistiques.",
      français: "Professeur de littérature et de grammaire française.",
      physique: "Enseignant en physique expérimentale et mécanique.",
      chimie: "Professeur de chimie organique et sciences des matériaux.",
      histoire: "Historien spécialisé dans la Révolution Française."
    };
    const domain = domains[Math.floor(Math.random() * domains.length)];

    document.getElementById('city').value = ["Paris", "Lyon", "Marseille", "Toulouse", "Bordeaux", "Grenoble"][Math.floor(Math.random() * 6)];
    document.getElementById('domain').value = domain;
    document.getElementById('description').value = descriptions[domain];

    diplomasContainer.innerHTML = '';
    experiencesContainer.innerHTML = '';

    const diplomaOptions = [
      ["Licence en Informatique", "Licence"],
      ["Master en Informatique", "Master"],
      ["Master Mathématiques", "Master"],
      ["Master Linguistique", "Master"],
      ["Doctorat en Physique", "Doctorat"],
      ["Doctorat en Chimie", "Doctorat"],
      ["Doctorat en Histoire", "Doctorat"]
    ];
    const diplCount = 1 + Math.floor(Math.random() * 2);
    for (let i = 0; i < diplCount; i++) {
      const [title, level] = diplomaOptions[Math.floor(Math.random() * diplomaOptions.length)];
      createDiplomaEntry(title, level);
    }

    const expOptions = [
      ["Professeur", "Sorbonne Université"],
      ["Formateur", "École 42"],
      ["Chercheur", "CNRS"],
      ["Chargé de cours", "Université de Lyon"],
      ["Data Scientist", "HEC Paris"]
    ];
    const expCount = 1 + Math.floor(Math.random() * 3);
    for (let i = 0; i < expCount; i++) {
      const [title, company] = expOptions[Math.floor(Math.random() * expOptions.length)];
      createExperienceEntry(title, company);
    }

    document.getElementById('pastCourseTitle').value = ["Programmation Python", "Analyse Mathématique", "Langue Française", "Chimie Organique", "Histoire Moderne"][Math.floor(Math.random() * 5)];
    document.getElementById('avgStars').value = (3.5 + Math.random() * 1.5).toFixed(1);

    document.getElementById('predictCourseTitle').value = ["Programmation Python", "Thermodynamique", "Langue Française", "Révolution Française", "Analyse Mathématique"][Math.floor(Math.random() * 5)];
    document.getElementById('predictCourseDesc').value = "Cours complet sur " + document.getElementById('predictCourseTitle').value.toLowerCase();
  }

  // ==== Écouteurs ====
  addDiplomaBtn.addEventListener('click', () => createDiplomaEntry());
  addExperienceBtn.addEventListener('click', () => createExperienceEntry());
  randomProfileBtn.addEventListener('click', generateRandomProfile);

  // ==== Formulaire ====
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    loader.style.display = 'block';
    result.style.display = 'none';

    const diplomas = Array.from(diplomasContainer.querySelectorAll('.entry')).map(d => ({
      title: d.querySelector('.diplomaTitle').value,
      level: d.querySelector('.diplomaLevel').value
    }));

    const experiences = Array.from(experiencesContainer.querySelectorAll('.entry')).map(e => ({
      title: e.querySelector('.expTitle').value,
      company: e.querySelector('.expCompany').value
    }));

    const teacher_profile = {
      description: document.getElementById('description').value,
      city: document.getElementById('city').value,
      diplomas,
      experiences,
      pastCourses: [{
        title: document.getElementById('pastCourseTitle').value,
        numberOfStars: parseFloat(document.getElementById('avgStars').value)
      }]
    };

    const course_to_predict = {
      title: document.getElementById('predictCourseTitle').value,
      description: document.getElementById('predictCourseDesc').value
    };

    const payload = { teacher_profile, course_to_predict };

    try {
      const response = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const data = await response.json();
      loader.style.display = 'none';

      if (!response.ok) {
        result.innerHTML = "❌ Erreur API : " + (data.detail || "inconnue");
      } else {
        result.innerHTML = `⭐ Note prédite : <span style="color:#00ffcc">${data.predicted_score}</span> / 5`;
      }
    } catch (err) {
      loader.style.display = 'none';
      result.innerHTML = "❌ Erreur réseau : " + err.message;
    }

    result.style.display = 'block';
  });
});
