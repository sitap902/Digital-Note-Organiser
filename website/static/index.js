function refreshHome() {
  window.location.href = "/";
}

function deleteNote(noteId) {
  fetch("/delete-note", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ noteId: noteId }),
  }).then(() => refreshHome());
}

function togglePin(noteId) {
  fetch("/toggle-pin", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ noteId: noteId }),
  }).then(() => refreshHome());
}
