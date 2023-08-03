function toggleCommentForm(postId) {
    var commentForm = document.getElementById("comment-form-" + postId);
    if (commentForm.style.display === "none") {
        commentForm.style.display = "block";
    } else {
        commentForm.style.display = "none";
    }
}

function toggleProfile() {
    const form = document.querySelector('.profile-pic')
    if (form.style.display === "none") {
        form.style.display = "block";
    } else {
        form.style.display = "none";
    }
}

function clearFile() {
    // Clear the selected file from the file input
    document.getElementById("file").value = "";
}
