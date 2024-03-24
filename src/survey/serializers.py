from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from survey.models import (
    Quiz,
    Question,
    QuizLogicType,
    Answer,
    Assignment,
)
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

    def to_representation(self, instance):
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
    def update(self, instance, validated_data):
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
        for user in users:
            user = get_object_or_404(User, pk=user.get("user").get("id"))
            Assignment.objects.create(
                user=user,
                quiz=instance,
            )

    @staticmethod
    def create_questions(data: list[dict], instance: Quiz) -> None:
        for question in data:
            if answers := question.pop("answers", None):
                question_instance = Question.objects.create(**question, quiz=instance)
                for answer in answers:
                    Answer.objects.create(**answer, question=question_instance)
