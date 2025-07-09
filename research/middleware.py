from django.conf import settings
from corsheaders.middleware import CorsMiddleware
from research.models import Website

class DynamicCorsMiddleware(CorsMiddleware):
    def __init__(self, get_response):
        super().__init__(get_response)
        self.update_allowed_origins()

    def update_allowed_origins(self):
        try:
            websites = Website.objects.all()
            # Assume domains are stored without protocol (e.g., "example.com")
            allowed_origins = [f"http://{website.domain}" for website in websites]
            # Add localhost for development
            allowed_origins.extend(["http://127.0.0.1:3000", "http://localhost:3000"])
            settings.CORS_ALLOWED_ORIGINS = allowed_origins
            print("Updated CORS origins:", allowed_origins)  # Debug log
        except Exception as e:
            print(f"Error updating CORS origins: {e}")
            settings.CORS_ALLOWED_ORIGINS = ["http://127.0.0.1:3000", "http://localhost:3000"]

    def __call__(self, request):
        self.update_allowed_origins()
        response = self.get_response(request)
        return response