# Mail Lab

Ce dépôt contient un projet complet pour la gestion des emails, comprenant un serveur backend, un client frontend basé sur Vue.js, et des outils pour tester et interagir avec des serveurs de messagerie.

## Structure du projet

```
api/
    main.py
mail_server/
    docker-compose.yml
    dns_lookup.py
    imap_list_and_save_attachments.py
    send_email_greenmail.py
vue-mailbox/
    ...
```

### Détails des dossiers

#### `api/`
Ce dossier contient une API FastAPI pour envoyer et recevoir des emails. Les principales fonctionnalités incluent :
- Envoi d'emails avec ou sans pièces jointes.
- Récupération des messages d'une boîte mail.
- Téléchargement des pièces jointes.

L'API est configurée pour fonctionner avec un serveur SMTP et IMAP local (par exemple, GreenMail).

#### `mail_server/`
Ce dossier contient des outils pour configurer et interagir avec des serveurs de messagerie :
- **`docker-compose.yml`** : Configuration pour lancer des serveurs de messagerie (MailHog et GreenMail) via Docker.
- **`send_email_greenmail.py`** : Script Python pour envoyer un email avec pièce jointe via GreenMail.
- **`imap_list_and_save_attachments.py`** : Script Python pour lister les emails et sauvegarder les pièces jointes depuis une boîte IMAP.
- **`dns_lookup.py`** : Script pour effectuer des recherches DNS (enregistrements MX et TXT).

#### `vue-mailbox/`
Ce dossier contient une application frontend développée avec Vue.js et Vite. Elle permet :
- L'envoi d'emails avec pièces jointes.
- La visualisation des emails reçus, y compris les pièces jointes.

### Fonctionnalités principales

#### Backend (`api/main.py`)
- **Envoi d'emails** : 
  - Endpoint : `POST /mail/send`
  - Endpoint : `POST /mail/send_multipart` (avec pièces jointes)
- **Récupération des emails** :
  - Endpoint : `GET /mail/messages`
  - Endpoint : `GET /mail/messages/{mid}`
- **Téléchargement des pièces jointes** :
  - Endpoint : `GET /mail/messages/{mid}/attachments/{index}`

#### Frontend (`vue-mailbox/`)
- **Composants principaux** :
  - `SendCompose.vue` : Formulaire pour composer et envoyer des emails.
  - `ListMail.vue` : Liste des emails reçus avec affichage des détails et téléchargement des pièces jointes.
- **Scripts** :
  - `npm run dev` : Démarre le serveur de développement.
  - `npm run build` : Compile et minifie l'application pour la production.
  - `npm run format` : Formate le code avec Prettier.

#### Serveurs de messagerie (`mail_server/docker-compose.yml`)
- **MailHog** : Serveur SMTP pour tester l'envoi d'emails.
- **GreenMail** : Serveur SMTP et IMAP pour tester l'envoi et la réception d'emails.

### Prérequis

- **Node.js** : Version 20.19.0 ou supérieure.
- **Python** : Version 3.10 ou supérieure.
- **Docker** : Pour exécuter les serveurs de messagerie.

### Installation

1. Clonez le dépôt :
   ```sh
   git clone <url-du-repo>
   cd mail_lab
   ```

2. Installez les dépendances du frontend :
   ```sh
   cd vue-mailbox
   npm install
   ```

3. Lancez les serveurs de messagerie :
   ```sh
   cd ../mail_server
   docker-compose up -d
   ```

4. Lancez l'API backend :
   ```sh
   cd ../api
   python -m uvicorn main:app --reload
   ```

5. Lancez le frontend :
   ```sh
   cd ../vue-mailbox
   npm run dev
   ```

### Utilisation

- Accédez à l'application frontend à l'adresse [http://localhost:5173](http://localhost:5173).
- Testez l'envoi et la réception d'emails via l'interface utilisateur.
- Consultez les logs des serveurs de messagerie pour déboguer si nécessaire.

### Scripts utiles

#### Python
- **Envoi d'email** : `python mail_server/send_email_greenmail.py`
- **Liste des emails et sauvegarde des pièces jointes** : `python mail_server/imap_list_and_save_attachments.py`
- **Recherche DNS** : `python mail_server/dns_lookup.py`

#### Node.js
- **Démarrage du frontend** : `npm run dev`
- **Compilation pour la production** : `npm run build`
- **Formatage du code** : `npm run format`

### Ressources

- [Documentation FastAPI](https://fastapi.tiangolo.com/)
- [Documentation Vue.js](https://vuejs.org/)
- [Documentation Vite](https://vitejs.dev/)
- [GreenMail](https://www.icegreen.com/greenmail/)

### Auteur

Ce projet est un exemple complet pour apprendre à travailler avec des emails en utilisant Python, Vue.js et Docker.

### Licence

Ce projet est sous licence MIT.