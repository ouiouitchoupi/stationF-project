// ==== Références DOM ====
const form = document.getElementById('predictForm');
const diplomasContainer = document.getElementById('diplomasContainer');
const experiencesContainer = document.getElementById('experiencesContainer');
const addDiplomaBtn = document.getElementById('addDiplomaBtn');
const addExperienceBtn = document.getElementById('addExperienceBtn');
const loader = document.getElementById('loader');
const result = document.getElementById('result');

// ==== Fonctions utilitaires ====
function createDiplomaEntry() {
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
      <option>Certificat de Développement Web</option>
    </select>
    <label>Niveau</label>
    <select class="diplomaLevel">
      <option>Certificat</option>
      <option>Licence</option>
      <option>Maîtrise</option>
      <option>Doctorat</option>
    </select>`;
  div.querySelector('.remove-btn').addEventListener('click', () => div.remove());
  diplomasContainer.appendChild(div);
}

function createExperienceEntry() {
  const div = document.createElement('div');
  div.className = 'entry';
  div.innerHTML = `
    <button type="button" class="remove-btn">🗑️</button>
    <label>Titre du poste</label>
    <select class="expTitle">
      <option>Professeur d'Informatique</option>
      <option>Formateur Web</option>
      <option>Data Scientist</option>
      <option>Chercheur</option>
    </select>
    <label>Établissement / Entreprise</label>
    <select class="expCompany">
      <option>École 42</option>
      <option>Sorbonne Université</option>
      <option>Polytechnique</option>
      <option>HEC Paris</option>
      <option>Université de Lyon</option>
      <option>Université de Toulouse</option>
      <option>Autre</option>
    </select>`;
  div.querySelector('.remove-btn').addEventListener('click', () => div.remove());
  experiencesContainer.appendChild(div);
}

// ==== Ajouts dynamiques ====
addDiplomaBtn.addEventListener('click', createDiplomaEntry);
addExperienceBtn.addEventListener('click', createExperienceEntry);

// ==== Formulaire : soumission ====
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
      console.error("Erreur API :", data);
      result.innerHTML = "❌ Erreur de prédiction : " + (data.detail || "inconnue");
      result.style.display = 'block';
      return;
    }

    if (typeof data.predicted_score === "undefined") {
      console.warn("⚠️ Réponse inattendue :", data);
      result.innerHTML = "❌ Réponse inattendue du serveur.";
    } else {
      result.innerHTML = `⭐ Note prédite : <span style="color:#00ffcc">${data.predicted_score}</span>`;
    }

    result.style.display = 'block';
  } catch (err) {
    loader.style.display = 'none';
    console.error("Erreur réseau :", err);
    result.innerHTML = "❌ Erreur réseau : " + err.message;
    result.style.display = 'block';
  }
});

// ==== Init par défaut ====
createDiplomaEntry();
createExperienceEntry();
