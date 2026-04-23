/**
 * VRButton.js — WebXR VR session button for Three.js knowledge base visualizations.
 *
 * Creates a button that initiates an immersive VR session for
 * 3D knowledge graph exploration. Based on Three.js VRButton pattern.
 */

export class VRButton {
  /**
   * Create a VR button element for the given renderer.
   * @param {import('three').WebGLRenderer} renderer - Three.js renderer
   * @param {Object} [options] - Configuration options
   * @param {string} [options.referenceSpaceType='local-floor'] - XR reference space type
   * @param {string[]} [options.optionalFeatures] - Optional XR features
   * @returns {HTMLButtonElement}
   */
  static createButton(renderer, options = {}) {
    const {
      referenceSpaceType = "local-floor",
      optionalFeatures = ["bounded-floor", "hand-tracking"],
    } = options;

    const button = document.createElement("button");
    button.style.cssText = `
      position: absolute; bottom: 20px; left: 50%;
      transform: translateX(-50%); padding: 12px 24px;
      border: 1px solid #fff; border-radius: 4px;
      background: rgba(0, 0, 0, 0.5); color: #fff;
      font: normal 14px sans-serif; cursor: pointer;
      z-index: 999; outline: none;
    `;

    function onSessionStarted(session) {
      session.addEventListener("end", onSessionEnded);
      renderer.xr.setReferenceSpaceType(referenceSpaceType);
      renderer.xr.setSession(session);
      button.textContent = "EXIT VR";
    }

    function onSessionEnded() {
      button.textContent = "ENTER VR";
    }

    if ("xr" in navigator) {
      navigator.xr.isSessionSupported("immersive-vr").then((supported) => {
        if (supported) {
          button.textContent = "ENTER VR";
          button.onclick = () => {
            const session = renderer.xr.getSession();
            if (session === null) {
              navigator.xr
                .requestSession("immersive-vr", {
                  optionalFeatures,
                })
                .then(onSessionStarted);
            } else {
              session.end();
            }
          };
        } else {
          button.textContent = "VR NOT SUPPORTED";
          button.disabled = true;
          button.style.opacity = "0.5";
          button.style.cursor = "not-allowed";
        }
      });
    } else {
      button.textContent = "WEBXR NOT AVAILABLE";
      button.disabled = true;
      button.style.opacity = "0.5";
      button.style.cursor = "not-allowed";
    }

    return button;
  }
}

export default VRButton;
