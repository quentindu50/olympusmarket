# AmbuTrack 🚑

**AmbuTrack** est une application web de gestion de transport médical (ambulances, VSL, taxis médicaux) développée avec Flask et SQLAlchemy.

## Fonctionnalités

- **Tableau de bord** — Vue d'ensemble des missions du jour, statistiques en temps réel
- **Gestion des transports** — Création, planification, suivi des missions (Taxi, VSL, Ambulance)
- **Base patients** — Dossiers patients avec N° sécu, ALD, mutuelle, médecin prescripteur
- **Gestion chauffeurs** — Documents, disponibilités, historique des courses
- **Parc véhicules** — Fiches véhicules, assurance, contrôle technique, maintenance
- **Facturation** — Génération de factures, télétransmission CPAM, gestion tiers-payant

## Stack technique

- **Backend** : Python / Flask
- **ORM** : Flask-SQLAlchemy (SQLite par défaut)
- **Frontend** : Bootstrap 5 + Bootstrap Icons

## Lancement rapide

```bash
pip install -r requirements.txt
cd src
python main.py
```

L'application sera disponible sur [http://localhost:5000](http://localhost:5000).

## Structure

```
src/
  app/
    models/        # Patient, Driver, Vehicle, Transport, Invoice, Establishment
    routes/        # dashboard, patients, drivers, vehicles, transports, invoices
    templates/     # Templates Jinja2 (Bootstrap 5)
    static/        # CSS
  main.py
requirements.txt
```

## Variables d'environnement

| Variable | Description | Défaut |
|---|---|---|
| `SECRET_KEY` | Clé secrète Flask | `ambutrack-dev-secret-key-2024` |
| `DATABASE_URL` | URL SQLAlchemy | SQLite local |
