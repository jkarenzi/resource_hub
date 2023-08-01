function toggleCommentForm(postId) {
    var commentForm = document.getElementById("comment-form-" + postId);
    if (commentForm.style.display === "none") {
        commentForm.style.display = "block";
    } else {
        commentForm.style.display = "none";
    }
}
