function openFile(file) {
    const reader = new FileReader();

    reader.onload = function(event) {
        const fileType = file.type;
        let content;

        if (fileType.startsWith('text/')) {
            content = `<pre>${event.target.result}</pre>`;
        } else if (fileType === 'application/pdf') {
            content = `<iframe src="${event.target.result}" width="100%" height="600px"></iframe>`;
        } else if (fileType.startsWith('image/')) {
            content = `<img src="${event.target.result}" alt="Image" style="max-width:100%; height:auto;">`;
        } else if (fileType.startsWith('video/')) {
            content = `<video controls width="100%"><source src="${event.target.result}" type="${fileType}">Your browser does not support the video tag.</video>`;
        } else if (fileType.startsWith('audio/')) {
            content = `<audio controls><source src="${event.target.result}" type="${fileType}">Your browser does not support the audio tag.</audio>`;
        } else {
            alert("File type is not supported");
            return;
        }

        const viewerWindow = window.open('', '_blank');
        viewerWindow.document.write(`
            <html>
                <head>
                    <title>File view</title>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 20px; }
                        iframe { border: none; }
                        {
                            height: fit-content;
                        }
                    </style>
                </head>
                <body>
                    ${content}
                </body>
            </html>
        `);
        viewerWindow.document.close();
    };

    if (file.type.startsWith('text/') || file.type === 'application/pdf') {
        reader.readAsDataURL(file);
    } else if (file.type.startsWith('image/') || file.type.startsWith('video/') || file.type.startsWith('audio/')) {
        reader.readAsDataURL(file);
    } else {
        alert("File type is nt supported");
    }
}


