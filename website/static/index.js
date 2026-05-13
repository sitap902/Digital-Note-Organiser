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

const pdfInput = document.getElementById("pdfInput");

if (pdfInput) {

  pdfInput.addEventListener("change", function () {

    const fileNameDisplay =
      document.getElementById("fileNameDisplay");

    if (this.files.length > 0) {

      fileNameDisplay.textContent =
        this.files[0].name;

    } else {

      fileNameDisplay.textContent =
        "No PDF selected";

    }

  });

}


const dropzone =
  document.getElementById("dropzone");

const pdfInput =
  document.getElementById("pdfInput");

const fileNameDisplay =
  document.getElementById("fileNameDisplay");

if (dropzone && pdfInput) {

  // CLICK SELECT

  pdfInput.addEventListener(
    "change",
    function () {

      if (this.files.length > 0) {

        fileNameDisplay.textContent =
          this.files[0].name;

      }

    }
  );

  // DRAG EVENTS

  [
    "dragenter",
    "dragover"
  ].forEach(eventName => {

    dropzone.addEventListener(
      eventName,
      e => {

        e.preventDefault();
        e.stopPropagation();

        dropzone.classList.add("dragover");

      }
    );

  });

  [
    "dragleave",
    "drop"
  ].forEach(eventName => {

    dropzone.addEventListener(
      eventName,
      e => {

        e.preventDefault();
        e.stopPropagation();

        dropzone.classList.remove("dragover");

      }
    );

  });

  // DROP FILE

  dropzone.addEventListener(
    "drop",
    e => {

      const files = e.dataTransfer.files;

      if (files.length > 0) {

        pdfInput.files = files;

        fileNameDisplay.textContent =
          files[0].name;

      }

    }
  );

}