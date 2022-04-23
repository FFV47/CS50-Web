const user = JSON.parse(document.getElementById("user-email").textContent);
const csrfToken = getCookie("csrftoken");

const MailApp = {
  composeForm: document.querySelector("#compose-form").cloneNode(true),
  readerView: document.querySelector("#reader-view").cloneNode(true),
};

document.addEventListener("DOMContentLoaded", function () {
  // Use buttons to toggle between views
  document.querySelector("#inbox").addEventListener("click", () => load_mailbox("inbox"));
  document.querySelector("#sent").addEventListener("click", () => load_mailbox("sent"));
  document
    .querySelector("#archive")
    .addEventListener("click", () => load_mailbox("archive"));
  document.querySelector("#compose").addEventListener("click", () => compose_email());

  // By default, load the inbox
  load_mailbox("inbox");
});

function compose_email(replyMail = null) {
  // change header button background color
  document
    .querySelectorAll(".btn.btn-sm.btn-outline-primary.mr-1")
    .forEach((element) => element.classList.remove("active"));

  document.querySelector("#compose").classList.add("active");

  // Clear previous event listeners
  document
    .querySelector("#compose-form")
    .replaceWith(MailApp.composeForm.cloneNode(true));

  const alert = document.querySelector("#response-error");
  alert.style.display = "none";
  const formRecipients = document.querySelector("#compose-recipients");
  const formSubject = document.querySelector("#compose-subject");
  const formBody = document.querySelector("#compose-body");

  // handle form fields filling
  if (replyMail) {
    formRecipients.value = replyMail.sender;
    formBody.value = `\n\nOn ${replyMail.timestamp}, ${replyMail.sender} wrote:\n\n${replyMail.body}`;

    // If subject already begins with Re: , no need to add it again
    if (/^Re: /.test(replyMail.subject)) {
      formSubject.value = replyMail.subject;
    } else {
      formSubject.value = "Re: " + replyMail.subject;
    }
  } else {
    // Clear out composition fields
    formRecipients.value = "";
    formSubject.value = "";
    formBody.value = "";
  }

  // handle form submitting
  document.querySelector("#compose-form").addEventListener(
    "submit",
    function (event) {
      event.preventDefault();

      const mailData = {
        recipients: formRecipients.value,
        subject: formSubject.value,
        body: formBody.value,
      };

      postMail(mailData).then((response) => {
        // handle alert message
        if (response.error) {
          alert.firstElementChild.firstElementChild.textContent = response.message;
          alert.style.display = "block";
          document.querySelector("#compose-view").scrollIntoView();
        } else {
          load_mailbox("sent", response.message);
        }
      });
    },
    {
      once: true,
    }
  );

  // Show compose view and hide other views
  document.querySelector("#emails-view").style.display = "none";
  document.querySelector("#reader-view").style.display = "none";
  document.querySelector("#compose-view").style.display = "block";
}

function load_mailbox(mailbox, alertMessage = "") {
  // change header button background color
  document
    .querySelectorAll(".btn.btn-sm.btn-outline-primary.mr-1")
    .forEach((element) => element.classList.remove("active"));

  document.querySelector("#" + mailbox).classList.add("active");

  // Fetch emails and update mailbox
  fetchMails(mailbox).then((emails) => {
    const alert = document.querySelector("#response-success");
    alert.style.display = "none";
    const emailList = document.querySelector("#email-list");
    emailList.textContent = "";

    // Email list rendering
    if (emails.length) {
      emails.map((email) => {
        const mailItem = renderEmailList(email);
        emailList.appendChild(mailItem);
      });
    } else {
      const empty = document.createElement("div");
      empty.classList.add("card", "card-body");
      empty.id = "empty";
      empty.textContent = "Mailbox Empty";
      emailList.appendChild(empty);
    }

    // Alert rendering
    if (alertMessage.length) {
      alert.textContent = alertMessage;
      alert.style.display = "block";
      document.querySelector("#emails-view").scrollIntoView();
      alert.addEventListener("click", () => (alert.style.display = "none"), {
        once: true,
      });
    }

    // Update mailbox name
    document.querySelector("#mailbox").textContent =
      mailbox.charAt(0).toUpperCase() + mailbox.slice(1);

    // Show the mailbox and hide other views
    document.querySelector("#emails-view").style.display = "block";
    document.querySelector("#reader-view").style.display = "none";
    document.querySelector("#compose-view").style.display = "none";
  });
}

function renderEmailList(email) {
  const subject = document.createElement("h5");
  subject.classList.add("mb-1");
  subject.textContent = email.subject;

  const date = document.createElement("small");
  date.textContent = email.timestamp.split(",")[0];

  const header = document.createElement("div");
  header.classList.add("d-flex", "w-100", "justify-content-between");
  header.appendChild(subject);
  header.appendChild(date);

  const sender = document.createElement("p");
  sender.classList.add("mb-1");
  sender.textContent = email.sender;

  const mailItem = document.createElement("a");
  mailItem.classList.add("list-group-item", "list-group-item-action");
  if (email.read) {
    mailItem.classList.add("list-group-item-secondary");
  }

  mailItem.addEventListener("click", () => loadReaderView(email.id));

  mailItem.appendChild(header);
  mailItem.appendChild(sender);

  return mailItem;
}

function loadReaderView(id) {
  fetchOneMail(id).then((email) => {
    // Mark clicked email as read
    if (!email.read) {
      putMail({ read: true }, email.id);
    }

    // Clear event listeners
    document
      .querySelector("#reader-view")
      .replaceWith(MailApp.readerView.cloneNode(true));

    // Hide the feedback alert
    const alert = document.querySelector("#archive-error");
    alert.style.display = "none";

    // Reply button
    const replyBtn = document.querySelector("#btn-reply");
    replyBtn.addEventListener("click", () => compose_email(email), { once: true });

    // Archive button
    const archiveBtn = document.querySelector("#btn-archiver");

    if (email.archived) {
      archiveBtn.textContent = "Unarchive";
    } else {
      archiveBtn.textContent = "Archive";
    }

    // If mailbox is 'Sent' hide the buttons
    if (email.sender === user.email) {
      replyBtn.style.display = "none";
      archiveBtn.style.display = "none";
    } else {
      replyBtn.style.display = "block";
      archiveBtn.style.display = "block";
    }

    // Archive button handler
    archiveBtn.addEventListener("click", function () {
      let data;
      if (email.archived) {
        data = { archived: false };
      } else {
        data = { archived: true };
      }
      putMail(data, email.id).then((response) => {
        if (response.error) {
          alert.firstElementChild.firstElementChild.textContent = response.message;
          alert.style.display = "block";
          document.querySelector("#reader-view").scrollIntoView();
        } else if (email.archived) {
          load_mailbox("inbox", "Email Unarchived");
        } else {
          load_mailbox("inbox", "Email Archived");
        }
      });
    });

    // Fill the reader with email data
    document.querySelector("#reader-subject").textContent = "Subject: " + email.subject;
    document.querySelector("#reader-sender").textContent = email.sender;
    document.querySelector("#reader-recipients").textContent =
      email.recipients.join(", ");
    document.querySelector("#reader-timestamp").textContent = email.timestamp;
    document.querySelector("#reader-body").textContent = email.body;

    // Show the reader and hide other views
    document.querySelector("#emails-view").style.display = "none";
    document.querySelector("#reader-view").style.display = "block";
    document.querySelector("#compose-view").style.display = "none";
  });
}

async function fetchMails(mailbox) {
  const response = await fetch(`/emails/${mailbox}`);
  const emails = await response.json();

  return emails;
}

async function fetchOneMail(id) {
  const response = await fetch(`/emails/${id}`, {
    headers: {
      "X-CSRFToken": csrfToken,
      "mode": "same-origin",
    },
  });
  const email = await response.json();

  return email;
}

async function postMail(mailData) {
  const dataString = JSON.stringify(mailData);
  try {
    const response = await fetch("/emails", {
      method: "POST",
      headers: {
        "Content-Type": "application/json; charset=utf-8",
        "X-CSRFToken": csrfToken,
        "mode": "same-origin",
      },
      body: dataString,
    });

    if (!response.ok) {
      const result = await response.json();
      throw new Error(result.error);
    }

    const result = await response.json();
    return {
      message: result.message,
      error: false,
    };
  } catch (e) {
    if (e instanceof TypeError) {
      return {
        message: Error("Network/Server failure"),
        error: true,
      };
    }
    return {
      message: e,
      error: true,
    };
  }
}

async function putMail(mailField, id) {
  const fieldString = JSON.stringify(mailField);
  try {
    const response = await fetch(`/emails/${id}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json; charset=utf-8",
        "X-CSRFToken": csrfToken,
        "mode": "same-origin",
      },
      body: fieldString,
    });

    if (!response.ok) {
      const result = await response.json();
      throw new Error(result.error);
    }

    return response.statusText;
  } catch (e) {
    if (e instanceof TypeError) {
      return {
        message: Error("Network/Server failure"),
        error: true,
      };
    }
    return {
      message: e,
      error: true,
    };
  }
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
