from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0005_userprofile"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="role",
            field=models.CharField(
                choices=[
                    ("student", "Öğrenci"),
                    ("staff", "Personel"),
                    ("volunteer", "Gönüllü"),
                ],
                default="student",
                max_length=20,
            ),
        ),
    ]
