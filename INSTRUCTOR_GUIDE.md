# Enterprise Learning Management System - Instructor Guide

This guide is designed for faculty and teaching assistants using the LMS to author courses, design curriculum, construct quizzes, track student attendance, and grade coursework.

---

## 🔑 Accessing the Instructor Portal

1. Navigate to the landing page and select **Instructor Portal** (or visit `/auth/login?portal=instructor`).
2. Log in with faculty credentials:
   - **Username**: `dr_hopper` / `dr_torvalds` / `prof_smith`
   - **Password**: `instructorpassword123`
3. You will land on the **Faculty Dashboard** (`/instructor/dashboard`).

---

## 📚 1. Course Authoring & Curriculum Management

### Creating a Course
1. Click **My Courses** (`/instructor/courses`) &rarr; **Create New Course**.
2. Complete the course details:
   - **Course Code**: e.g., `CS-202`
   - **Course Title**: e.g., `Advanced Algorithms & Data Structures`
   - **Category & Difficulty**: Computer Science, Intermediate
   - **Duration & Capacity**: 30 hours, 50 students
3. Save to create the draft course.

### Building Curriculum Units
1. Navigate to **Curriculum Builder** (`/instructor/courses/<id>/curriculum`).
2. **Add Modules**: Group your syllabus into thematic modules (e.g., `Module 1: Binary Trees`).
3. **Add Lessons**: Within each module, add lessons:
   - Select Lesson Type: `Text / Markdown`, `Video`, `Quiz`, or `Lab`.
   - Author rich lesson content with code blocks and callouts.
   - Attach study guides, PDF documents, or starter code.

---

## 📝 2. Question Bank & Quizzes

### Question Bank
* Author reusable questions: Multiple Choice (Single), Multi-select, True/False, and Short Answer.
* Set mark values, explanations, and difficulty levels.

### Quiz Builder
1. Navigate to **Course Quizzes** (`/instructor/courses/<id>/quizzes`).
2. Set quiz title, passing percentage (e.g., 60%), and time limit (e.g., 20 minutes).
3. Link questions from the question bank to the quiz.
4. Quizzes are automatically evaluated by the LMS assessment engine upon student submission.

---

## 📋 3. Coursework Assignments & Grading

1. Navigate to **Assignments** (`/instructor/courses/<id>/assignments`).
2. Define assignment title, due date, maximum marks, and instructions.
3. Once students submit work, navigate to the **Submissions Queue**:
   - Inspect student code and text submissions.
   - Enter score, letter grade (`A`, `B`, `C`, etc.), and personalized feedback.
   - Submit grade to update student transcripts instantly.

---

## 📅 4. Class Attendance Tracking

1. Navigate to **Attendance** (`/instructor/courses/<id>/attendance`).
2. Click **Create Attendance Session** (specifying date and session topic).
3. Mark each enrolled student as `Present`, `Late`, `Absent`, or `Excused`.
4. The system calculates running attendance percentages for every student.

---

## 📊 5. Course Gradebook

1. Navigate to **Course Gradebook** (`/instructor/courses/<id>/gradebook`).
2. View aggregated student performance across assignments, quizzes, and attendance.
3. Automatically compute final cumulative grades with a single click.
