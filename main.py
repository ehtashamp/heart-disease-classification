# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from yellowbrick.cluster import KElbowVisualizer
from matplotlib.colors import ListedColormap
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder, OneHotEncoder
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, GradientBoostingClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, mean_absolute_error, mean_squared_error, r2_score
import warnings

warnings.filterwarnings('ignore')

# Load the data
df = pd.read_csv("/content/heart.csv")

# Encode categorical columns
categorical_cols = ['sex', 'cp', 'fbs', 'restecg', 'exang', 'slope', 'ca', 'thal', 'dataset']
label_encoders = {}
for col in categorical_cols:
    label_encoders[col] = LabelEncoder()
    df[col] = label_encoders[col].fit_transform(df[col])

# Data information
df.head()
df.info()
df.shape

# Basic statistics
df['age'].describe()

# Custom color palette
custom_colors = ["#FF5733", "#3366FF", "#33FF57"]
sns.histplot(df['age'], kde=True, color="#FF5733", palette=custom_colors)
plt.axvline(df['age'].mean(), color='Red')
plt.axvline(df['age'].median(), color='Green')
plt.axvline(df['age'].mode()[0], color='Blue')
plt.show()

# Plotly histogram
fig = px.histogram(data_frame=df, x='age', color='sex')
fig.show()

# Percentage calculations for 'sex' column
male_count = df['sex'].value_counts().get(1, 0)
female_count = df['sex'].value_counts().get(0, 0)
total_count = male_count + female_count
male_percentage = (male_count / total_count) * 100
female_percentage = (female_count / total_count) * 100
print(f'Male percentage in the data: {male_percentage:.2f}%')
print(f'Female percentage in the data: {female_percentage:.2f}%')
difference_percentage = ((male_count - female_count) / female_count) * 100
print(f'Males are {difference_percentage:.2f}% more than females in the data.')

# Group by 'sex' and 'age'
print(df.groupby('sex')['age'].value_counts())

# Counts for 'dataset' column
print(df['dataset'].value_counts())

# Plotly bar chart for 'dataset' column
fig = px.bar(df, x='dataset', color='sex')
fig.show()

# Histogram for 'age' column colored by 'dataset'
fig = px.histogram(data_frame=df, x='age', color='dataset')
fig.show()

# Summary statistics for 'trestbps' column
print(df['trestbps'].describe())

# Missing values in 'trestbps' column
print(f"Percentage of missing values in 'trestbps' column: {df['trestbps'].isnull().sum() / len(df) * 100:.2f}%")

# Impute missing values in 'trestbps' column using IterativeImputer
imputer1 = IterativeImputer(max_iter=10, random_state=42)
df['trestbps'] = imputer1.fit_transform(df[['trestbps']])
print(f"Missing values in 'trestbps' column after imputation: {df['trestbps'].isnull().sum()}")

# Impute other columns
imputer2 = IterativeImputer(max_iter=10, random_state=42)
df['ca'] = imputer2.fit_transform(df[['ca']])
df['oldpeak'] = imputer2.fit_transform(df[['oldpeak']])
df['chol'] = imputer2.fit_transform(df[['chol']])
df['thalch'] = imputer2.fit_transform(df[['thalch']])

# Check for missing values
print(df.isnull().sum().sort_values(ascending=False))

# Function to impute missing values in categorical columns
def impute_categorical_missing_data(df, col):
    df_null = df[df[col].isnull()]
    df_not_null = df[df[col].notnull()]
    X = df_not_null.drop(col, axis=1)
    y = df_not_null[col]

    # Encode categorical columns
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y)

    imputer = IterativeImputer(estimator=RandomForestClassifier(random_state=16), max_iter=10, random_state=42)
    imputer.fit(X, y)
    df[col] = imputer.transform(df[col].values.reshape(-1, 1)).flatten()

    return df

# Function to impute missing values in continuous columns
def impute_continuous_missing_data(df, col):
    df_null = df[df[col].isnull()]
    df_not_null = df[df[col].notnull()]
    X = df_not_null.drop(col, axis=1)
    y = df_not_null[col]

    imputer = IterativeImputer(estimator=RandomForestRegressor(random_state=16), max_iter=10, random_state=42)
    imputer.fit(X, y)
    df[col] = imputer.transform(df[col].values.reshape(-1, 1)).flatten()

    return df

# Check for missing values after imputation
print(df.isnull().sum().sort_values(ascending=False))

# Boxen plots for columns
sns.set(rc={"axes.facecolor": "#87CEEB", "figure.facecolor": "#EEE8AA"})
palette = ["#682F2F", "#9E726F", "#D6B2B1", "#B9C0C9", "#9F8A78", "#F3AB60"]
plt.figure(figsize=(10, 8))
for i, col in enumerate(df.columns):
    plt.subplot(3, 2, i + 1)
    sns.boxenplot(x=df[col], color=palette[i % len(palette)])
    plt.title(col)
plt.tight_layout()
plt.show()

# Remove rows with 'trestbps' value of 0
df = df[df['trestbps'] != 0]

# Encode 'dataset' column
df['dataset'] = LabelEncoder().fit_transform(df['dataset'])

# Split data into X and y
X = df.drop('num', axis=1)
y = df['num']

# Encode categorical columns
categorical_cols = ['thal', 'ca', 'slope', 'exang', 'restecg', 'fbs', 'cp', 'sex']
for col in categorical_cols:
    X[col] = LabelEncoder().fit_transform(X[col])

# Split data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)

# Define models
models = [
    ('Logistic Regression', LogisticRegression(random_state=42)),
    ('KNeighbors Classifier', KNeighborsClassifier()),
    ('Support Vector Machine', SVC(random_state=42)),
    ('Decision Tree Classifier', DecisionTreeClassifier(random_state=42)),
    ('Random Forest', RandomForestClassifier(random_state=42)),
    ('AdaBoost Classifier', AdaBoostClassifier(random_state=42)),
    ('Gradient Boosting', GradientBoostingClassifier(random_state=42)),
    ('XGBoost', XGBClassifier(random_state=42)),
    ('LightGBM', LGBMClassifier(random_state=42)),
    ('GaussianNB', GaussianNB())
]

best_model = None
best_accuracy = 0.0
from sklearn.pipeline import Pipeline
# Iterate over the models and evaluate their performance
for name, model in models:
    pipeline = Pipeline([
        ('model', model)
    ])
    scores = cross_val_score(pipeline, X_train, y_train, cv=5)
    mean_accuracy = scores.mean()
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model: {name}")
    print(f"Cross Validation Accuracy: {mean_accuracy}")
    print(f"Test Accuracy: {accuracy}\n")
    if accuracy > best_accuracy:
        best_accuracy = accuracy
        best_model = pipeline

print("Best Model:", best_model)

# Hyperparameter tuning
def hyperparameter_tuning(X, y, categorical_columns, models):
    results = {}
    X_encoded = X.copy()
    label_encoder = LabelEncoder()
    for col in categorical_columns:
        X_encoded[col] = label_encoder.fit_transform(X_encoded[col])

    X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=0.2, random_state=42)

    for model_name, model in models.items():
        param_grid = {}
        if model_name == 'Logistic Regression':
            param_grid = {'C': [0.1, 1, 10, 100]}
        elif model_name == 'KNN':
            param_grid = {'n_neighbors': [3, 5, 7, 9]}
        elif model_name == 'Gaussian Naive Bayes':
            param_grid = {'var_smoothing': np.logspace(-9, 0, 10)}
        elif model_name == 'SVM':
            param_grid = {'C': [0.1, 1, 10], 'kernel': ['linear', 'rbf']}
        elif model_name == 'Decision Tree':
            param_grid = {'max_depth': [None, 10, 20, 30], 'min_samples_split': [2, 5, 10]}
        elif model_name == 'Random Forest':
            param_grid = {'n_estimators': [50, 100, 200], 'max_depth': [None, 10, 20, 30]}
        elif model_name == 'AdaBoost':
            param_grid = {'n_estimators': [50, 100, 200], 'learning_rate': [0.01, 0.1, 1]}
        elif model_name == 'Gradient Boosting':
            param_grid = {'n_estimators': [50, 100, 200], 'learning_rate': [0.01, 0.1, 1]}
        elif model_name == 'XGBoost':
            param_grid = {'n_estimators': [50, 100, 200], 'learning_rate': [0.01, 0.1, 1]}
        else:
            continue

        grid_search = GridSearchCV(model, param_grid, cv=5, scoring='accuracy')
        grid_search.fit(X_train, y_train)
        best_params = grid_search.best_params_
        best_estimator = grid_search.best_estimator_
        y_pred = best_estimator.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        results[model_name] = {'best_params': best_params, 'accuracy': accuracy}

    return results

# Define models for tuning
models_for_tuning = {
    'Logistic Regression': LogisticRegression(),
    'KNN': KNeighborsClassifier(),
    'Gaussian Naive Bayes': GaussianNB(),
    'SVM': SVC(),
    'Decision Tree': DecisionTreeClassifier(),
    'Random Forest': RandomForestClassifier(),
    'AdaBoost': AdaBoostClassifier(),
    'Gradient Boosting': GradientBoostingClassifier(),
    'XGBoost': XGBClassifier()
}

# Perform hyperparameter tuning
results = hyperparameter_tuning(X, y, categorical_cols, models_for_tuning)
print(results)
