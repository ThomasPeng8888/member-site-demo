(function () {
    "use strict";

    function clamp(value, min, max) {
        return Math.max(min, Math.min(value, max));
    }

    function ready(callback) {
        if (document.readyState === "loading") {
            document.addEventListener("DOMContentLoaded", callback);
        } else {
            callback();
        }
    }

    ready(function () {
        const input = document.getElementById("id_image");
        if (!input) return;

        const cropX = document.getElementById("id_crop_x");
        const cropY = document.getElementById("id_crop_y");
        const cropW = document.getElementById("id_crop_w");
        const cropH = document.getElementById("id_crop_h");
        if (!cropX || !cropY || !cropW || !cropH) return;

        const panel = document.createElement("div");
        panel.className = "guppyguppy-product-cropper";
        panel.innerHTML = `
            <div class="guppyguppy-cropper-heading">
                <div>
                    <strong>商品圖片正方形裁切</strong>
                    <p>選擇照片後，拖曳白色正方形框調整商品主體位置；右下角圓點可調整裁切大小。儲存後會自動輸出正方形圖片、壓縮並套用品牌浮水印。</p>
                </div>
                <span class="guppyguppy-cropper-badge">1:1 官方商品圖</span>
            </div>
            <div class="guppyguppy-cropper-layout">
                <div class="guppyguppy-cropper-stage-wrap">
                    <div class="guppyguppy-cropper-stage">
                        <img alt="商品裁切預覽" />
                        <div class="guppyguppy-crop-box"><span class="guppyguppy-crop-handle" aria-hidden="true"></span></div>
                    </div>
                </div>
                <div class="guppyguppy-crop-preview-panel">
                    <strong>前台預覽</strong>
                    <div class="guppyguppy-crop-preview"><img alt="正方形預覽" /></div>
                    <p class="guppyguppy-cropper-note">商品列表、商品詳情與浮水印位置都會以此正方形為基準。</p>
                </div>
            </div>
        `;

        const imageFieldRow = input.closest(".form-row") || input.parentElement;
        imageFieldRow.insertAdjacentElement("afterend", panel);

        const stage = panel.querySelector(".guppyguppy-cropper-stage");
        const image = stage.querySelector("img");
        const box = stage.querySelector(".guppyguppy-crop-box");
        const handle = stage.querySelector(".guppyguppy-crop-handle");
        const preview = panel.querySelector(".guppyguppy-crop-preview");
        const previewImage = preview.querySelector("img");

        let imageUrl = null;
        let boxState = { left: 0, top: 0, size: 0 };
        let interaction = null;

        function clearCropValues() {
            cropX.value = "";
            cropY.value = "";
            cropW.value = "";
            cropH.value = "";
        }

        function imageRect() {
            return {
                width: image.clientWidth,
                height: image.clientHeight,
            };
        }

        function setBox(next) {
            const rect = imageRect();
            const minSize = Math.max(40, Math.min(rect.width, rect.height) * 0.18);
            const maxSize = Math.max(minSize, Math.min(rect.width, rect.height));
            const size = clamp(next.size, minSize, maxSize);
            const left = clamp(next.left, 0, rect.width - size);
            const top = clamp(next.top, 0, rect.height - size);

            boxState = { left, top, size };
            box.style.left = `${left}px`;
            box.style.top = `${top}px`;
            box.style.width = `${size}px`;
            box.style.height = `${size}px`;
            updateValuesAndPreview();
        }

        function updateValuesAndPreview() {
            const rect = imageRect();
            if (!rect.width || !rect.height || !boxState.size) return;

            const x = boxState.left / rect.width;
            const y = boxState.top / rect.height;
            const w = boxState.size / rect.width;
            const h = boxState.size / rect.height;

            cropX.value = x.toFixed(6);
            cropY.value = y.toFixed(6);
            cropW.value = w.toFixed(6);
            cropH.value = h.toFixed(6);

            const previewSize = preview.clientWidth || 144;
            const scale = previewSize / boxState.size;
            previewImage.src = image.src;
            previewImage.style.width = `${rect.width * scale}px`;
            previewImage.style.height = `${rect.height * scale}px`;
            previewImage.style.transform = `translate(${-boxState.left * scale}px, ${-boxState.top * scale}px)`;
        }

        function resetCropBox() {
            const rect = imageRect();
            if (!rect.width || !rect.height) return;

            const size = Math.min(rect.width, rect.height) * 0.82;
            setBox({
                left: (rect.width - size) / 2,
                top: (rect.height - size) / 2,
                size: size,
            });
        }

        function pointerPosition(event) {
            const point = event.touches && event.touches.length ? event.touches[0] : event;
            return { x: point.clientX, y: point.clientY };
        }

        function startInteraction(event, mode) {
            if (!panel.classList.contains("is-active")) return;
            event.preventDefault();
            const point = pointerPosition(event);
            interaction = {
                mode,
                startX: point.x,
                startY: point.y,
                startLeft: boxState.left,
                startTop: boxState.top,
                startSize: boxState.size,
            };
            window.addEventListener("pointermove", moveInteraction);
            window.addEventListener("pointerup", stopInteraction);
        }

        function moveInteraction(event) {
            if (!interaction) return;
            event.preventDefault();
            const point = pointerPosition(event);
            const dx = point.x - interaction.startX;
            const dy = point.y - interaction.startY;

            if (interaction.mode === "resize") {
                const delta = Math.max(dx, dy);
                setBox({
                    left: interaction.startLeft,
                    top: interaction.startTop,
                    size: interaction.startSize + delta,
                });
                return;
            }

            setBox({
                left: interaction.startLeft + dx,
                top: interaction.startTop + dy,
                size: interaction.startSize,
            });
        }

        function stopInteraction() {
            interaction = null;
            window.removeEventListener("pointermove", moveInteraction);
            window.removeEventListener("pointerup", stopInteraction);
        }

        box.addEventListener("pointerdown", function (event) {
            if (event.target === handle) return;
            startInteraction(event, "move");
        });
        handle.addEventListener("pointerdown", function (event) {
            startInteraction(event, "resize");
        });

        input.addEventListener("change", function () {
            clearCropValues();

            const file = input.files && input.files[0];
            if (!file) {
                panel.classList.remove("is-active");
                return;
            }

            if (!file.type || !file.type.startsWith("image/")) {
                panel.classList.remove("is-active");
                return;
            }

            if (imageUrl) {
                URL.revokeObjectURL(imageUrl);
            }

            imageUrl = URL.createObjectURL(file);
            image.onload = function () {
                panel.classList.add("is-active");
                window.requestAnimationFrame(resetCropBox);
            };
            image.src = imageUrl;
        });

        window.addEventListener("resize", function () {
            if (panel.classList.contains("is-active")) {
                // Keep the same relative crop after the preview resizes.
                const old = {
                    x: parseFloat(cropX.value || "0"),
                    y: parseFloat(cropY.value || "0"),
                    w: parseFloat(cropW.value || "0"),
                };
                const rect = imageRect();
                if (rect.width && rect.height && old.w > 0) {
                    setBox({
                        left: old.x * rect.width,
                        top: old.y * rect.height,
                        size: old.w * rect.width,
                    });
                }
            }
        });

        const form = input.closest("form");
        if (form) {
            form.addEventListener("submit", updateValuesAndPreview);
        }
    });
})();
