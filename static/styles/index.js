const dropzone = document.querySelector('.drop-zone');
const browseButton = document.querySelector('.browseButton');
const fileInput = document.querySelector('#fileInput');
const bgprogress = document.querySelector('.bgprogress');
const percentDiv = document.querySelector('#progpercent')



dropzone.addEventListener('dragover',(e)=>{
    e.preventDefault()

    if (!dropzone.classList.contains('dragged')){
        dropzone.classList.add('dragged');
    }
    
});

dropzone.addEventListener('dragleave',()=>{
    dropzone.classList.remove('dragged');
});
dropzone.addEventListener('drop',(e)=>{
    e.preventDefault()
    dropzone.classList.remove('dragged');
    const files = e.dataTransfer.files
    console.table(e);
    if (files.length) {
       fileInput.files = files; 
       uploadFile();
    } 
});

fileInput.addEventListener('change',()=>{
    uploadFile();
})

browseButton.addEventListener('click',()=>{
    fileInput.click();
});

