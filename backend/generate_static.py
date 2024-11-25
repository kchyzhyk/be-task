import os
from django.conf import settings
from django.template.loader import render_to_string
from django.core.wsgi import get_wsgi_application
import warnings

warnings.filterwarnings("ignore", category=UserWarning, message=".*csrf_token.*")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
application = get_wsgi_application()

output_dir = os.path.join(settings.BASE_DIR, 'backend/docs')
os.makedirs(output_dir, exist_ok=True)

rendered_content = render_to_string('tasks/base.html',
    # {'csrf_token': ''}
)

with open(os.path.join(output_dir, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(rendered_content)
