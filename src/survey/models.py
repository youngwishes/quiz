from django.db import models


class AccessType(models.TextChoices):
    ALWAYS = "Always"
    LIMITED = "Limited"


class QuizLogicType(models.TextChoices):
    DEPENDENT = "Dependent"
    SEQUENTIAL = "Sequential"


class Quiz(models.Model):
    title = models.CharField("заголовок", max_length=256)
    execution_time = models.IntegerField()
    type = models.CharField("тип", choices=QuizLogicType.choices)
    access = models.CharField("тип доступа", choices=AccessType.choices)
    expiration_date = models.DateField(null=True)

    @property
    def conditions(self) -> dict:
        return {"expiration_date": self.expiration_date, "access": self.access}

    @conditions.setter
    def conditions(self, conditions: dict) -> None:
        self.access = conditions.get("access")
        self.expiration_date = conditions.get("expiration_date")


class Question(models.Model):
    class Type(models.TextChoices):
        SINGLE = "Single"
        FREE = "Free"

    _id = models.IntegerField()
    text = models.TextField("текст")
    type = models.CharField("тип вопроса", choices=Type.choices)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions", null=True)


class Answer(models.Model):
    text = models.TextField()
    next_question_id = models.IntegerField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers", null=True)


class Assignment(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="assignment")
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="assignment")
