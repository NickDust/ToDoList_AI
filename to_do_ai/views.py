from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import TaskModel
from .serializers import TaskSerializer, AiTaskSerializer, RegisterSerializer
from django.shortcuts import get_object_or_404
from openai import OpenAI
import json
from drf_spectacular.utils import extend_schema
import os
from dotenv import load_dotenv
load_dotenv()

class TaskView(APIView):

    def get(self, request):
        data = TaskModel.objects.filter(user=request.user).order_by("-id")
        if not data:
            return Response({"Message": "You have no tasks!."})
        serializer = TaskSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @extend_schema(
            request=TaskSerializer
    )
    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            task = serializer.validated_data["task"]
            due_date = serializer.validated_data["due_date"]
            return Response({"message": f"the task({task}) due in {due_date} created."}, status=status.HTTP_201_CREATED)
        
class DetailTaskView(APIView):

    @extend_schema(
            request=TaskSerializer
    )
    def patch(self, request, pk):
        task = get_object_or_404(TaskModel, pk=pk, user=request.user)
        
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer._errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        task = get_object_or_404(TaskModel, pk=pk, user=request.user)
        task.delete()
        return Response({"message": "Task deleted."}, status=status.HTTP_204_NO_CONTENT)
    

class TaskAIView(APIView):

    @extend_schema(
        request= AiTaskSerializer
    )
    def post(self,request):
        serializer = AiTaskSerializer(data=request.data)
        if serializer.is_valid():
            text = serializer.validated_data["text"]
            base_url = "https://api.aimlapi.com/v1"
            api_key = os.getenv("AI_KEY") 

            system_prompt = """
        You are an assistant that transforms free text into structured TODO tasks.  
        Given a user input, extract a list of small, actionable tasks.  

        Rules:
        - Output ONLY valid JSON. Do not include any explanations, comments, or extra text.
        - Follow this schema exactly:

        {
        "tasks": [
            {
            "task": "string",
            "description" : "string" (if given otherwise empty string)
            "due_date": "YYYY-MM-DD",
            "priority": "low|medium|high"
            }
        ]
        }

        - If the user does not specify a due_date, choose a sensible one within the next 30 days.
        - If multiple tasks are mentioned, return each as a separate object in the array.
        - Priorities:  
        - "high" for urgent or critical tasks,  
        - "medium" for normal tasks,  
        - "low" for optional or nice-to-have tasks.
        - Never return empty arrays: if you cannot extract tasks, return at least one generic task with today's date.
        - Do not include markdown formatting, backticks, or any text outside of the JSON object.
        """
            user_prompt = text

            api = OpenAI(api_key=api_key, base_url=base_url)
            completion = api.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
                ],
            temperature=0.3,
            max_tokens=200,
            )
            response = completion.choices[0].message.content
            print(response)
            try:
                parsed_outp = json.loads(response)
                task = parsed_outp.get("tasks", [])
                for t in task:
                    t["user"] = request.user.id
            except json.JSONDecodeError:
                return Response({"Error": "Invalis JSON from AI", "raw" : response}, status=status.HTTP_400_BAD_REQUEST)
            
            if not task:
                return Response({"Error": "No task found in AI output"}, status=status.HTTP_400_BAD_REQUEST)

            ser = TaskSerializer(data=task, many=True)
            ser.is_valid(raise_exception=True)
            ser.save()
            return Response(ser.data, status=status.HTTP_201_CREATED)

class RegisterView(APIView):

    @extend_schema(request=RegisterSerializer)
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User created correctly."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)