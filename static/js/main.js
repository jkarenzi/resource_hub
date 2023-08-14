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

function toggleRateForm(id) {
    var commentForm = document.getElementById("rate-form-" + id);
    if (commentForm.style.display === "none") {
        commentForm.style.display = "block";
    } else {
        commentForm.style.display = "none";
    }
}


function myFun() {
    const dropMenu = document.querySelector('.drop');
    if (dropMenu.style.display === 'flex') {
        dropMenu.style.display = 'none';
    } else {
        dropMenu.style.display = 'flex';
    }
}

function myFun2() {
    const searchbar = document.querySelector('.searchbar');
    const left_arrow = document.querySelector('.cancel-search');
    const navElement = document.querySelector('nav');
    const search = document.querySelector('.search_icon');
    const headerElement = document.querySelector('header');
    const headerLink = headerElement.querySelector('a');
    if (searchbar.style.display === 'none') {
        searchbar.style.display = 'flex';
        left_arrow.style.display = 'flex';
        navElement.style.display = 'none';
        search.style.display = 'none';
        headerLink.style.display = 'none';
    } else {
        searchbar.style.display = 'none';
    }
}

function myFun3() {
    const navElement = document.querySelector('nav');
    const searchbar = document.querySelector('.searchbar');
    const left_arrow = document.querySelector('.cancel-search');
    const search = document.querySelector('.search_icon');
    const headerElement = document.querySelector('header');
    const headerLink = headerElement.querySelector('a');
    if (searchbar.style.display === 'flex') {
        navElement.style.display = 'flex';
        searchbar.style.display = 'none';
        left_arrow.style.display = 'none';
        search.style.display = 'flex';
        headerLink.style.display = 'flex';
    }
}
