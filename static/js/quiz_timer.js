/**
 * Quiz and Exam Interactive Countdown Timer
 */

function initQuizTimer(durationMinutes, timerElementId, formId) {
  let remainingSeconds = durationMinutes * 60;
  const timerDisplay = document.getElementById(timerElementId);
  const quizForm = document.getElementById(formId);

  if (!timerDisplay || !quizForm) return;

  function updateTimer() {
    const minutes = Math.floor(remainingSeconds / 60);
    const seconds = remainingSeconds % 60;
    const formatted = `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;

    timerDisplay.textContent = formatted;

    if (remainingSeconds <= 120) {
      timerDisplay.style.color = "#ef4444";
      timerDisplay.style.fontWeight = "bold";
    }

    if (remainingSeconds <= 0) {
      clearInterval(interval);
      alert("Time is up! Submitting your answers automatically.");
      quizForm.submit();
    }

    remainingSeconds--;
  }

  updateTimer();
  const interval = setInterval(updateTimer, 1000);
}
