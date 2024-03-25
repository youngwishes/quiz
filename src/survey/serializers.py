from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from survey.models import (
    Quiz,
    Question,
    QuizLogicType,
    Answer,
    Assignment,
    QuestionType,
)
from survey.validation import QuizValidationService
from users.models import User


class AssignmentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="user.id")

    class Meta:
        model = Assignment
        fields = ("id",)


class ConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ("access", "expiration_date")


class LogicSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=QuizLogicType.choices)

    def to_representation(self, instance: str) -> str:
        return instance


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ("text", "next_question_id")


class QuestionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ("_id", "text", "type")


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, required=False)
    id = serializers.IntegerField(source="_id")

    class Meta:
        model = Question
        fields = ("id", "text", "type", "answers")

    def to_representation(self, instance: Question) -> dict:
        representation = super().to_representation(instance)
        if representation.get("type") == QuestionType.FREE:
            del representation["answers"]
        return representation


class QuizListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = "id", "title"


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)
    assignment = AssignmentSerializer(many=True)
    conditions = ConditionSerializer()
    logic = LogicSerializer(source="type")

    class Meta:
        model = Quiz
        fields = (
            "id",
            "title",
            "execution_time",
            "questions",
            "logic",
            "conditions",
            "assignment"
        )

    def to_representation(self, instance: Quiz) -> dict:
        representation = super().to_representation(instance)
        if representation.get("conditions").get("expiration_date") is None:
            del representation["conditions"]["expiration_date"]
        return representation

    @atomic
    def create(self, validated_data: dict) -> Quiz:
        questions = validated_data.pop("questions")
        users = validated_data.pop("assignment")
        validated_data["type"] = validated_data.pop("type").get("type")
        instance = super().create(validated_data)
        self.create_questions(questions, instance)
        self.create_assignment(users, instance)
        return instance

    @atomic
    def update(self, instance: Quiz, validated_data: dict) -> Quiz:
        questions = validated_data.pop("questions")
        users = validated_data.pop("assignment")
        validated_data["type"] = validated_data.pop("type").get("type")
        instance = super().update(instance, validated_data)
        instance.questions.all().delete()
        instance.assignment.all().delete()
        self.create_assignment(users, instance)
        self.create_questions(questions, instance)
        return instance

    @staticmethod
    def create_assignment(users: list[dict], instance: Quiz) -> None:
        user_ids = set(assignment.get("user").get("id") for assignment in users)
        for user_id in user_ids:
            user = get_object_or_404(User, pk=user_id)
            Assignment.objects.create(
                user=user,
                quiz=instance,
            )

    @staticmethod
    def create_questions(data: list[dict], instance: Quiz) -> None:
        service = QuizValidationService(data=data)
        service.run_validation_checkers()
        for question in data:
            answers = question.pop("answers", [])
            question_instance = Question.objects.create(**question, quiz=instance)
            for answer in answers:
                Answer.objects.create(**answer, question=question_instance)
