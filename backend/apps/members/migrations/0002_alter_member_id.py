
import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("members", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="member",
            name="id",
        ),
        migrations.AddField(
            model_name="member",
            name="id",
            field=models.UUIDField(
                primary_key=True,
                default=uuid.uuid4,
                editable=False,
                serialize=False,
            ),
        ),
    ]
