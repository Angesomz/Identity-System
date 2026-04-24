/**
 * Resizes an image file to a maximum width/height while maintaining aspect ratio.
 * @param {File} file - The image file to resize.
 * @param {number} maxWidth - Maximum width (default 1920).
 * @param {number} maxHeight - Maximum height (default 1080).
 * @returns {Promise<string>} - A promise that resolves to the resized image as a Base64 Data URL.
 */
export const resizeImage = (file, maxWidth = 1920, maxHeight = 1080) => {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = (event) => {
            const img = new Image();
            img.src = event.target.result;
            img.onload = () => {
                let width = img.width;
                let height = img.height;

                // Calculate new dimensions
                if (width > height) {
                    if (width > maxWidth) {
                        height *= maxWidth / width;
                        width = maxWidth;
                    }
                } else {
                    if (height > maxHeight) {
                        width *= maxHeight / height;
                        height = maxHeight;
                    }
                }

                // Draw to canvas
                const canvas = document.createElement('canvas');
                canvas.width = width;
                canvas.height = height;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0, width, height);

                // Return as Base64
                resolve(canvas.toDataURL('image/jpeg', 0.9)); // 90% quality JPEG
            };
            img.onerror = (err) => reject(err);
        };
        reader.onerror = (err) => reject(err);
    });
};
