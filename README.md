# IMR-AI Project Setup and Deployment Guide

This document provides comprehensive instructions for setting up, running, and deploying the IMR-AI project, which includes two Django apps: **Chatbot** and **Chatsearch**. The project uses the **Google Generative AI Model 2.0 Flash** for its AI capabilities. Follow the steps below to configure the environment, set up the database, ingest data, and deploy the applications.

---

## 1. Project Overview

IMR-AI is a Django-based project with two primary applications:
- **Chatsearch**: A search-based application accessible at `http://127.0.0.1:8000/`.
- **Chatbot**: A chatbot application that can be integrated into external websites and tested at:
  - `http://127.0.0.1:8000/test/`
  - `http://127.0.0.1:8000/test1/`

This guide covers environment setup, database configuration, data ingestion, API key management, and deployment instructions.

---

## 2. Environment Setup

### 2.1 Prerequisites
- **Python Version**: Use Python 3.11.
- **Dependencies**: Install the required packages listed in `requirements.txt`.
- **AI Model**: The project uses the **Google Generative AI Model 2.0 Flash**. Ensure you have a valid API key for this model.

### 2.2 Install Dependencies
1. Ensure you are in the project directory.
2. Run the following command to install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## 3. Database Configuration

To prevent crashes, configure the database properly in the following files:
- `settings.py`
- `views.py`
- `ingest_to_db.py`

### Steps:
1. Replace the database configuration in the above files with the appropriate database table details for your system or the website’s database.
2. Ensure you have PostgreSQL installed and running.
3. Update the database settings with your database name, user, password, host, and port.

**Example Configuration in `settings.py`:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_database_name',
        'USER': 'your_database_user',
        'PASSWORD': 'your_database_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

**Note**: Failure to configure the database correctly may cause the project to crash.

---

## 4. Django Setup and Migrations

Follow these steps to set up the Django project and apply migrations:

### 4.1 Make Migrations
This creates migration files for any changes made to your models.
```bash
python manage.py makemigrations
```

### 4.2 Apply Migrations
This applies the migration files to your PostgreSQL database.
```bash
python manage.py migrate
```

### 4.3 Create a Superuser
Create a superuser to access the Django admin panel.
```bash
python manage.py createsuperuser
```
Follow the prompts to set up the username, email, and password.

---

## 5. Running the Development Server

Start the Django development server to run the project locally:
```bash
python manage.py runserver
```

### Access Points:
- **Project URL**: `http://127.0.0.1:8000/`
- **Admin Panel**: `http://127.0.0.1:8000/admin/`
- **Chatbot Test Pages**:
  - `http://127.0.0.1:8000/test/`
  - `http://127.0.0.1:8000/test1/`

---

## 6. Chatbot Integration

To integrate the **Chatbot** application into an external website:

1. **Add Website in Django Admin**:
   - Log in to the admin panel at `http://127.0.0.1:8000/admin/`.
   - Add the website you want to integrate the chatbot with.
   - A code snippet will be generated in the admin panel.

2. **Embed Code Snippet**:
   - Copy the generated code snippet.
   - Paste it into the HTML code of the target website.

3. **CORS Policy Configuration**:
   - Update CORS policies in the following files to allow communication between the chatbot and the website:
     - `chatbot.js`
     - `settings.py`
     - `manage.py`
   - Example CORS configuration in `settings.py`:
     ```python
     CORS_ALLOWED_ORIGINS = [
         "http://your-website.com",
         "http://127.0.0.1:8000",
     ]
     ```

---

## 7. Data Ingestion

Once the database is configured, ingest data through the Django admin panel:

1. **Access the Admin Panel**:
   - Visit `http://127.0.0.1:8000/admin/`.
   - Navigate to the relevant section for data ingestion.

2. **Ingestion Options**:
   - **Bulk Upload**: Upload multiple data entries at once.
   - **Regular Upload**: Upload data manually.
   - **Sitemap Ingestion**: Enter a sitemap URL to automatically fetch and ingest URLs.

3. **Chatsearch API Key**:
   - For **Chatsearch**, update the API key in `index.html`:
     - Each website in the admin panel has a unique API key.
     - Copy the API key for the desired website and paste it into `index.html`.
   - Alternatively, create a new website entry in the admin panel, copy the new API key, and ingest data specific to **Chatsearch**.

4. **Managing Google Generative AI Model 2.0 Flash API Key**:
   - The project uses the **Google Generative AI Model 2.0 Flash** for AI functionality.
   - If the API key reaches its usage limit, replace it with a new valid API key:
     - Obtain a new API key from the Google Cloud Console.
     - Update the API key in the relevant configuration files (e.g., `views.py` or environment variables).
     - Example configuration in `views.py`:
       ```python
       GOOGLE_API_KEY = 'your_new_google_api_key'
       ```
   - Ensure the new API key is active to avoid disruptions in AI functionality.

---

## 8. Optimization

To optimize the AI’s performance:
- Modify the prompt in `views.py` to suit your requirements for the **Google Generative AI Model 2.0 Flash**.
- Example modification in `views.py`:
  ```python
  AI_PROMPT = "Provide concise and accurate answers based on the ingested data using Google Generative AI Model 2.0 Flash."
  ```

---

## 9. Deployment Notes

When deploying the project to a production environment:
- Ensure CORS policies are correctly configured in `chatbot.js`, `settings.py`, and `manage.py`.
- Verify database connectivity in the production environment.
- Update the Google Generative AI Model 2.0 Flash API key if necessary, especially if usage limits are reached.
- Use a production-ready server (e.g., Gunicorn with Nginx) instead of the development server.
- Example Gunicorn command:
  ```bash
  gunicorn --workers 3 your_project_name.wsgi:application
  ```

---

## 10. Troubleshooting

- **Project Crashes**: Ensure the database is properly configured in `settings.py`, `views.py`, and `ingest_to_db.py`.
- **CORS Issues**: Check CORS settings in `settings.py` and ensure the website’s domain is listed in `CORS_ALLOWED_ORIGINS`.
- **API Key Errors**: Verify that the correct **Google Generative AI Model 2.0 Flash** API key is used in `index.html` for **Chatsearch** and other relevant files. Replace the API key if usage limits are exhausted.
- **AI Functionality Issues**: Ensure the Google API key is valid and has not exceeded its quota.

---

## 11. URLs Summary

- **Chatsearch**: `http://127.0.0.1:8000/`
- **Chatbot Test Pages**:
  - `http://127.0.0.1:8000/test/`
  - `http://127.0.0.1:8000/test1/`
- **Admin Panel**: `http://127.0.0.1:8000/admin/`

---

## 12. Additional Notes

- Regularly check the Django admin panel for updates to data ingestion or website integration.
- Monitor the **Google Generative AI Model 2.0 Flash** API key usage in the Google Cloud Console and replace it if the limit is exhausted.
- For API-related queries or integrations, refer to [xAI’s API documentation](https://x.ai/api) or the Google Cloud documentation for the Generative AI Model.

For further assistance, contact the project administrator or refer to the official Django and Google Cloud documentation.


bellow i am attaching the project report.
[IMR-AI_Technology_and_Implementation_Overview_Enhanced.docx](https://github.com/user-attachments/files/21135611/IMR-AI_Technology_and_Implementation_Overview_Enhanced.docx)
