# Documentation du Processus de Machine Learning pour la Prédiction des Ratings

## Table des matières
1. [Préparation des données](#1-préparation-des-données)
2. [Modélisation](#2-modélisation)
3. [Évaluation et Monitoring](#3-évaluation-et-monitoring)
4. [Infrastructure et Dépendances](#4-infrastructure-et-dépendances)
5. [Guide d'utilisation](#5-guide-dutilisation)

## 1. Préparation des données

### Features utilisées
- **Features numériques** :
  - trust_score
  - diff_experience_review
  - diff_review_response
  - num_special_characters
  - num_uppercase_characters
  - total_characters
  - positive_emojis
  - negative_emojis
  - nombre_point_intero
  - nombre_point_exclam

- **Features textuelles** :
  - commentaire_en (transformé via TF-IDF)

### Pipeline de prétraitement
1. **Gestion des valeurs manquantes**
   - Features numériques : SimpleImputer (stratégie: median)
   - Features textuelles : Remplacement par chaîne vide

2. **Standardisation**
   - StandardScaler pour les features numériques

3. **Vectorisation du texte**
   - TF-IDF Vectorizer
   - max_features=1000
   - ngram_range=(1, 2)

### Fichiers générés
- `X_train.npz` : Features d'entraînement
- `X_test.npz` : Features de test
- `y_train.npy` : Labels d'entraînement
- `y_test.npy` : Labels de test
- `numeric_imputer.pkl` : Imputer pour les valeurs manquantes
- `scaler.pkl` : Standardiseur
- `tfidf_vectorizer.pkl` : Vectoriseur TF-IDF

### Exécution du pipeline
1. **Préparation des données**

## 2. Modélisation

### Modèles testés
1. **Random Forest**
   ```python
   RandomForestClassifier(
       n_estimators=[100, 200],
       max_depth=[10, 20, None],
       min_samples_split=[2, 5]
   )
   ```

2. **Régression Logistique**
   ```python
   LogisticRegression(
       C=[0.1, 1.0, 10.0],
       max_iter=[1000]
   )
   ```

3. **XGBoost**
   ```python
   XGBClassifier(
       n_estimators=[100, 200],
       max_depth=[3, 5, 7],
       learning_rate=[0.01, 0.1]
   )
   ```

4. **LightGBM**
   ```python
   LGBMClassifier(
       n_estimators=[100, 200],
       num_leaves=[31, 127],
       learning_rate=[0.01, 0.1]
   )
   ```

## 3. Évaluation et Monitoring

### Métriques d'évaluation
- Accuracy
- Classification Report (precision, recall, f1-score)
- Matrice de confusion

### Outils de monitoring
1. **MLflow**
   - Tracking des expériences
   - Logging des métriques et paramètres
   - Stockage des artifacts
   - Interface web de visualisation

2. **Evidently**
   - Data Drift Analysis
   - Target Drift Analysis
   - Data Quality Analysis
   - Classification Performance Metrics

3. **SHAP**
   - Feature Importance Analysis
   - Individual Prediction Explanation
   - Global Model Interpretation

### Artifacts générés
- `evidently_report_{model_name}.html`
- `shap_summary_{model_name}.png`
- `confusion_matrix_{model_name}.png`

## 4. Infrastructure et Dépendances

### Requirements

txt
numpy
pandas
scikit-learn
scipy
xgboost
lightgbm
mlflow
evidently
shap
seaborn
matplotlib

### Base de données MLflow
- URI: "sqlite:///mlflow.db"
- Experiment name: "Rating_Prediction"

## 5. Guide d'utilisation

### Installation
bash
pip install -r requirements.txt

### Configuration
bash
mlflow server --host 0.0.0.0 --port 5000 --backend-store sqlite:///mlflow.db

