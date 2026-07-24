(() => {
  "use strict";

  const deps = window.SkillSystemSpatialDeps;
  if (!deps) return;

  const { THREE, OrbitControls, GLTFLoader } = deps;

  const create = (tag, options = {}) => {
    const node = document.createElement(tag);
    if (options.className) node.className = options.className;
    if (options.text !== undefined) node.textContent = String(options.text);
    Object.entries(options.attrs || {}).forEach(([name, value]) => {
      if (value !== undefined && value !== null) {
        node.setAttribute(name, String(value));
      }
    });
    return node;
  };

  const append = (parent, ...children) => {
    children.filter(Boolean).forEach((child) => parent.appendChild(child));
    return parent;
  };

  const cssColor = (name, fallback) =>
    getComputedStyle(document.documentElement).getPropertyValue(name).trim() ||
    fallback;

  const colorForKind = (kind) => {
    const map = {
      selection: ["--rc-yellow", "#edd400"],
      non_manifold: ["--rc-red", "#f92672"],
      boundary: ["--rc-orange", "#fd971f"],
      degenerate: ["--rc-red-deep", "#a40000"],
      added: ["--rc-green-bright", "#a6e22e"],
      removed: ["--rc-red", "#f92672"],
      changed: ["--rc-blue", "#729fcf"],
      unknown: ["--rc-plum", "#ad7fa8"],
    };
    const pair = map[kind] || map.unknown;
    return cssColor(pair[0], pair[1]);
  };

  const decodeBase64 = (value) => {
    const binary = atob(value);
    const bytes = new Uint8Array(binary.length);
    for (let index = 0; index < binary.length; index += 1) {
      bytes[index] = binary.charCodeAt(index);
    }
    return bytes.buffer;
  };

  const geometryFromModel = (data) => {
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute(
      "position",
      new THREE.Float32BufferAttribute(data.positions, 3),
    );
    if (Array.isArray(data.indices) && data.indices.length) {
      geometry.setIndex(data.indices);
    }
    if (Array.isArray(data.normals) && data.normals.length) {
      geometry.setAttribute(
        "normal",
        new THREE.Float32BufferAttribute(data.normals, 3),
      );
    } else {
      geometry.computeVertexNormals();
    }
    geometry.computeBoundingBox();
    geometry.computeBoundingSphere();
    geometry.userData.faceIds = data.face_ids || [];
    geometry.userData.vertexIds = data.vertex_ids || [];
    return geometry;
  };

  const parseAsset = async (asset) => {
    if (asset.format === "buffer_geometry") {
      if (!asset.geometry) throw new Error("buffer_geometry asset에 geometry가 없습니다.");
      const group = new THREE.Group();
      const mesh = new THREE.Mesh(geometryFromModel(asset.geometry));
      mesh.name = "BufferGeometry";
      group.add(mesh);
      return group;
    }

    const loader = new GLTFLoader();
    let data;
    if (asset.format === "glb" && asset.data_base64) {
      data = decodeBase64(asset.data_base64);
    } else if (asset.format === "gltf" && asset.data_text) {
      data = asset.data_text;
    } else {
      throw new Error(
        "GLB/glTF asset은 self-contained data_base64 또는 data_text가 필요합니다.",
      );
    }

    return new Promise((resolve, reject) => {
      loader.parse(
        data,
        "",
        (gltf) => resolve(gltf.scene || gltf.scenes[0]),
        (error) => reject(error),
      );
    });
  };

  const visitMeshes = (object, visitor) => {
    object?.traverse((child) => {
      if (child.isMesh) visitor(child);
    });
  };

  const makeNormals = (mesh, length) => {
    const position = mesh.geometry.getAttribute("position");
    const normal = mesh.geometry.getAttribute("normal");
    if (!position || !normal) return null;
    const points = [];
    const origin = new THREE.Vector3();
    const direction = new THREE.Vector3();
    const normalMatrix = new THREE.Matrix3().getNormalMatrix(mesh.matrixWorld);
    for (let index = 0; index < position.count; index += 1) {
      origin.fromBufferAttribute(position, index).applyMatrix4(mesh.matrixWorld);
      direction
        .fromBufferAttribute(normal, index)
        .applyMatrix3(normalMatrix)
        .normalize();
      points.push(
        origin.x,
        origin.y,
        origin.z,
        origin.x + direction.x * length,
        origin.y + direction.y * length,
        origin.z + direction.z * length,
      );
    }
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute(
      "position",
      new THREE.Float32BufferAttribute(points, 3),
    );
    return new THREE.LineSegments(
      geometry,
      new THREE.LineBasicMaterial({
        color: colorForKind("changed"),
        depthTest: false,
        transparent: true,
        opacity: 0.82,
      }),
    );
  };

  const overlayObject = (rootObject, overlay) => {
    const firstMesh = [];
    visitMeshes(rootObject, (mesh) => firstMesh.push(mesh));
    const source = firstMesh[0];
    if (!source) return null;
    source.updateWorldMatrix(true, false);
    const position = source.geometry.getAttribute("position");
    const index = source.geometry.getIndex();
    if (!position) return null;
    const color = colorForKind(overlay.kind);
    const group = new THREE.Group();
    group.name = `overlay:${overlay.kind}:${overlay.label}`;

    if (Array.isArray(overlay.edges) && overlay.edges.length >= 2) {
      const points = [];
      for (let cursor = 0; cursor + 1 < overlay.edges.length; cursor += 2) {
        const a = overlay.edges[cursor];
        const b = overlay.edges[cursor + 1];
        if (a >= position.count || b >= position.count) continue;
        const va = new THREE.Vector3().fromBufferAttribute(position, a);
        const vb = new THREE.Vector3().fromBufferAttribute(position, b);
        va.applyMatrix4(source.matrixWorld);
        vb.applyMatrix4(source.matrixWorld);
        points.push(va.x, va.y, va.z, vb.x, vb.y, vb.z);
      }
      const geometry = new THREE.BufferGeometry();
      geometry.setAttribute(
        "position",
        new THREE.Float32BufferAttribute(points, 3),
      );
      group.add(
        new THREE.LineSegments(
          geometry,
          new THREE.LineBasicMaterial({
            color,
            depthTest: false,
            transparent: true,
            opacity: 0.98,
          }),
        ),
      );
    }

    if (Array.isArray(overlay.vertices) && overlay.vertices.length) {
      const points = [];
      overlay.vertices.forEach((vertexIndex) => {
        if (vertexIndex >= position.count) return;
        const point = new THREE.Vector3()
          .fromBufferAttribute(position, vertexIndex)
          .applyMatrix4(source.matrixWorld);
        points.push(point.x, point.y, point.z);
      });
      const geometry = new THREE.BufferGeometry();
      geometry.setAttribute(
        "position",
        new THREE.Float32BufferAttribute(points, 3),
      );
      group.add(
        new THREE.Points(
          geometry,
          new THREE.PointsMaterial({
            color,
            size: 7,
            sizeAttenuation: false,
            depthTest: false,
          }),
        ),
      );
    }

    if (Array.isArray(overlay.faces) && overlay.faces.length) {
      const points = [];
      const faceCount = index ? Math.floor(index.count / 3) : Math.floor(position.count / 3);
      overlay.faces.forEach((faceIndex) => {
        if (!Number.isInteger(faceIndex) || faceIndex < 0 || faceIndex >= faceCount) return;
        for (let corner = 0; corner < 3; corner += 1) {
          const sourceIndex = index
            ? index.getX(faceIndex * 3 + corner)
            : faceIndex * 3 + corner;
          if (sourceIndex >= position.count) return;
          const point = new THREE.Vector3()
            .fromBufferAttribute(position, sourceIndex)
            .applyMatrix4(source.matrixWorld);
          points.push(point.x, point.y, point.z);
        }
      });
      const geometry = new THREE.BufferGeometry();
      geometry.setAttribute(
        "position",
        new THREE.Float32BufferAttribute(points, 3),
      );
      group.add(
        new THREE.Mesh(
          geometry,
          new THREE.MeshBasicMaterial({
            color,
            side: THREE.DoubleSide,
            transparent: true,
            opacity: 0.45,
            depthTest: false,
          }),
        ),
      );
    }
    return group.children.length ? group : null;
  };

  const applyMaterials = (object, clippingPlane) => {
    visitMeshes(object, (mesh) => {
      const originalColor = mesh.material?.color?.clone();
      mesh.userData.reportOriginalMaterial = mesh.material;
      mesh.material = new THREE.MeshStandardMaterial({
        color: originalColor || cssColor("--rc-text", "#d3d7cf"),
        metalness: 0.05,
        roughness: 0.68,
        side: THREE.DoubleSide,
        clippingPlanes: [clippingPlane],
        clipShadows: true,
      });
    });
  };

  const mount = (host, visual, callbacks = {}) => {
    const shell = create("div", { className: "rc-spatial-shell" });
    const stage = create("div", { className: "rc-spatial-stage" });
    const inspector = create("aside", {
      className: "rc-spatial-inspector",
      attrs: { "aria-label": "3D inspector" },
    });
    const canvas = create("canvas", {
      attrs: { "aria-label": "Interactive 3D report viewport" },
    });
    const hud = create("div", {
      className: "rc-spatial-hud",
      text:
        visual.caption ||
        "Orbit: drag · Pan: right-drag · Zoom: wheel · Select: click",
    });
    append(stage, canvas, hud);
    append(shell, stage, inspector);
    host.appendChild(shell);

    const renderer = new THREE.WebGLRenderer({
      canvas,
      antialias: true,
      alpha: false,
      powerPreference: "high-performance",
    });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    // Keep local clipping disabled until the user moves the plane. This avoids compiling the
    // clipping uniform against a not-yet-fitted camera during the first asynchronous asset load.
    renderer.localClippingEnabled = false;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(42, 1, 0.001, 100000);
    camera.position.set(2.4, 1.8, 2.8);
    const controls = new OrbitControls(camera, canvas);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;

    const clippingPlane = new THREE.Plane(new THREE.Vector3(1, 0, 0), 100000);
    const ambient = new THREE.HemisphereLight(0xffffff, 0x303030, 1.8);
    const key = new THREE.DirectionalLight(0xffffff, 2.2);
    key.position.set(4, 7, 6);
    scene.add(ambient, key);

    const world = new THREE.Group();
    const overlayRoot = new THREE.Group();
    const helperRoot = new THREE.Group();
    scene.add(world, overlayRoot, helperRoot);

    let currentObject = null;
    let currentStateIndex = -1;
    let ghostObject = null;
    let selectedMesh = null;
    let selectedFace = null;
    let isolated = false;
    let wireframe = false;
    let verticesVisible = false;
    let normalsVisible = false;
    let clippingEnabled = false;

    const readout = create("div", {
      className: "rc-spatial-readout",
      text: "selection: none\nsource indices: authoritative data only",
    });

    const toolbarGroup = (title) => {
      const group = create("section", { className: "rc-toolbar-group" });
      group.appendChild(create("span", { className: "rc-toolbar-label", text: title }));
      inspector.appendChild(group);
      return group;
    };

    const viewGroup = toolbarGroup("View");
    const viewTools = create("div", { className: "rc-tool-grid" });
    const tool = (text, action, pressed = false) => {
      const button = create("button", {
        className: "rc-tool",
        text,
        attrs: {
          type: "button",
          "data-action": action,
          "aria-pressed": String(pressed),
        },
      });
      viewTools.appendChild(button);
      return button;
    };
    const resetButton = tool("Reset", "reset");
    const fitButton = tool("Fit", "fit");
    const wireButton = tool("Wire", "wire");
    const vertexButton = tool("Vertices", "vertices");
    const normalButton = tool("Normals", "normals");
    const isolateButton = tool("Isolate object", "isolate");
    const hideButton = tool("Hide object", "hide");
    const ghostButton = tool("Ghost previous", "ghost");
    append(viewGroup, viewTools);

    const states =
      Array.isArray(visual.states) && visual.states.length
        ? visual.states
        : [{ id: "current", label: "Current", asset: visual.asset }];
    let stateSelect = null;
    if (states.length > 1) {
      const stateGroup = toolbarGroup("Mutation timeline");
      stateSelect = create("select", { attrs: { "aria-label": "Spatial state" } });
      states.forEach((state, index) => {
        const option = create("option", {
          text: state.label,
          attrs: { value: String(index) },
        });
        stateSelect.appendChild(option);
      });
      stateGroup.appendChild(stateSelect);
    } else {
      ghostButton.disabled = true;
    }

    const clipGroup = toolbarGroup("Clipping plane · X");
    const clipRange = create("input", {
      attrs: {
        type: "range",
        min: "-100",
        max: "100",
        value: "100",
        step: "1",
        "aria-label": "X clipping plane",
      },
    });
    clipGroup.appendChild(clipRange);

    const overlayRows = [];
    if (Array.isArray(visual.overlays) && visual.overlays.length) {
      const overlayGroup = toolbarGroup("Authoritative overlays");
      const list = create("div", { className: "rc-overlay-list" });
      visual.overlays.forEach((overlay, index) => {
        const row = create("label", { className: "rc-overlay-row" });
        const check = create("input", {
          attrs: { type: "checkbox", checked: "checked" },
        });
        const dot = create("span", { className: "rc-overlay-dot" });
        dot.style.setProperty("--overlay-color", colorForKind(overlay.kind));
        append(row, check, dot, create("span", { text: overlay.label }));
        check.addEventListener("change", () => {
          const object = overlayRows[index]?.object;
          if (object) object.visible = check.checked;
        });
        overlayRows.push({ overlay, check, object: null });
        list.appendChild(row);
      });
      overlayGroup.appendChild(list);
    }

    const selectionGroup = toolbarGroup("Selection");
    selectionGroup.appendChild(readout);

    const clearObject = (object) => {
      if (!object) return;
      object.traverse((child) => {
        child.geometry?.dispose?.();
        if (Array.isArray(child.material)) {
          child.material.forEach((material) => material.dispose?.());
        } else {
          child.material?.dispose?.();
        }
      });
      object.removeFromParent();
    };

    const sceneBox = () => {
      const box = new THREE.Box3();
      if (currentObject) box.expandByObject(currentObject, true);
      if (box.isEmpty()) box.setFromCenterAndSize(new THREE.Vector3(), new THREE.Vector3(2, 2, 2));
      return box;
    };

    const fit = () => {
      const box = sceneBox();
      const sphere = box.getBoundingSphere(new THREE.Sphere());
      const radius = Math.max(sphere.radius, 0.001);
      const distance = radius / Math.sin(THREE.MathUtils.degToRad(camera.fov / 2));
      const direction = new THREE.Vector3(1, 0.72, 1.1).normalize();
      camera.position.copy(sphere.center).addScaledVector(direction, distance * 1.12);
      camera.near = Math.max(distance / 1000, 0.0001);
      camera.far = distance * 100;
      camera.updateProjectionMatrix();
      controls.target.copy(sphere.center);
      controls.update();
      clippingPlane.constant = radius * 4;
      clipRange.value = "100";
      clippingEnabled = false;
      renderer.localClippingEnabled = false;
    };

    const rebuildHelpers = () => {
      while (helperRoot.children.length) clearObject(helperRoot.children[0]);
      if (!currentObject) return;
      const box = sceneBox();
      const size = box.getSize(new THREE.Vector3()).length() || 1;
      visitMeshes(currentObject, (mesh) => {
        if (verticesVisible) {
          const points = new THREE.Points(
            mesh.geometry.clone(),
            new THREE.PointsMaterial({
              color: colorForKind("selection"),
              size: 4,
              sizeAttenuation: false,
              depthTest: false,
            }),
          );
          points.matrixAutoUpdate = false;
          points.matrix.copy(mesh.matrixWorld);
          helperRoot.add(points);
        }
        if (normalsVisible) {
          const normals = makeNormals(mesh, size * 0.025);
          if (normals) helperRoot.add(normals);
        }
      });
    };

    const rebuildOverlays = () => {
      while (overlayRoot.children.length) clearObject(overlayRoot.children[0]);
      overlayRows.forEach((entry) => {
        const stateId = states[currentStateIndex]?.id;
        if (
          Array.isArray(entry.overlay.state_refs) &&
          !entry.overlay.state_refs.includes(stateId)
        ) {
          entry.object = null;
          entry.check.disabled = true;
          return;
        }
        entry.check.disabled = false;
        entry.object = overlayObject(currentObject, entry.overlay);
        if (entry.object) {
          entry.object.visible = entry.check.checked;
          overlayRoot.add(entry.object);
        }
      });
    };

    const configureObject = (object, opacity = 1) => {
      object.updateMatrixWorld(true);
      applyMaterials(object, clippingPlane);
      visitMeshes(object, (mesh) => {
        mesh.material.wireframe = wireframe;
        mesh.material.transparent = opacity < 1;
        mesh.material.opacity = opacity;
      });
    };

    const loadGhost = async () => {
      clearObject(ghostObject);
      ghostObject = null;
      if (ghostButton.getAttribute("aria-pressed") !== "true" || currentStateIndex <= 0) {
        return;
      }
      ghostObject = await parseAsset(states[currentStateIndex - 1].asset);
      ghostObject.name = "Previous state ghost";
      configureObject(ghostObject, 0.18);
      visitMeshes(ghostObject, (mesh) => {
        mesh.material.color.set(colorForKind("removed"));
        mesh.material.depthWrite = false;
      });
      world.add(ghostObject);
    };

    const setState = async (index) => {
      currentStateIndex = index;
      selectedMesh = null;
      selectedFace = null;
      isolated = false;
      clearObject(currentObject);
      clearObject(ghostObject);
      currentObject = null;
      ghostObject = null;
      readout.textContent = "selection: none\nsource indices: authoritative data only";
      const object = await parseAsset(states[index].asset);
      object.name = states[index].label;
      configureObject(object);
      currentObject = object;
      world.add(object);
      rebuildHelpers();
      rebuildOverlays();
      fit();
      await loadGhost();
    };

    const setPressed = (button, value) =>
      button.setAttribute("aria-pressed", String(value));

    resetButton.addEventListener("click", () => {
      camera.position.set(2.4, 1.8, 2.8);
      controls.target.set(0, 0, 0);
      controls.update();
      fit();
    });
    fitButton.addEventListener("click", fit);
    wireButton.addEventListener("click", () => {
      wireframe = !wireframe;
      setPressed(wireButton, wireframe);
      visitMeshes(currentObject, (mesh) => {
        mesh.material.wireframe = wireframe;
      });
    });
    vertexButton.addEventListener("click", () => {
      verticesVisible = !verticesVisible;
      setPressed(vertexButton, verticesVisible);
      rebuildHelpers();
    });
    normalButton.addEventListener("click", () => {
      normalsVisible = !normalsVisible;
      setPressed(normalButton, normalsVisible);
      rebuildHelpers();
    });
    isolateButton.addEventListener("click", () => {
      if (!selectedMesh || !currentObject) return;
      isolated = !isolated;
      setPressed(isolateButton, isolated);
      visitMeshes(currentObject, (mesh) => {
        mesh.visible = !isolated || mesh === selectedMesh;
      });
    });
    hideButton.addEventListener("click", () => {
      if (!selectedMesh) return;
      selectedMesh.visible = false;
      selectedMesh = null;
      selectedFace = null;
      readout.textContent = "selection: hidden object\nReset state to restore visibility";
    });
    ghostButton.addEventListener("click", async () => {
      const active = ghostButton.getAttribute("aria-pressed") !== "true";
      setPressed(ghostButton, active);
      await loadGhost();
    });
    stateSelect?.addEventListener("change", async () => {
      await setState(Number(stateSelect.value));
    });
    clipRange.addEventListener("input", () => {
      const box = sceneBox();
      const sphere = box.getBoundingSphere(new THREE.Sphere());
      const normalized = Number(clipRange.value) / 100;
      clippingEnabled = normalized < 0.999;
      renderer.localClippingEnabled = clippingEnabled;
      clippingPlane.constant = clippingEnabled
        ? sphere.radius * normalized
        : sphere.radius * 4;
    });

    const raycaster = new THREE.Raycaster();
    const pointer = new THREE.Vector2();
    canvas.addEventListener("pointerup", (event) => {
      if (!currentObject || event.button !== 0) return;
      const rect = canvas.getBoundingClientRect();
      pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
      raycaster.setFromCamera(pointer, camera);
      const intersections = raycaster.intersectObject(currentObject, true);
      const hit = intersections.find((item) => item.object?.isMesh);
      if (!hit) return;
      selectedMesh = hit.object;
      selectedFace = hit.faceIndex;
      const faceIds = selectedMesh.geometry.userData.faceIds || [];
      const sourceFaceId = faceIds[selectedFace] ?? selectedFace;
      const point = hit.point;
      readout.textContent = [
        `object: ${selectedMesh.name || "(unnamed)"}`,
        `face index: ${selectedFace}`,
        `source face id: ${sourceFaceId ?? "unavailable"}`,
        `position: ${point.x.toFixed(4)}, ${point.y.toFixed(4)}, ${point.z.toFixed(4)}`,
      ].join("\n");
    });

    const updateTheme = () => {
      scene.background = new THREE.Color(cssColor("--rc-bg-deep", "#2e3436"));
      renderer.setClearColor(scene.background, 1);
      visitMeshes(currentObject, (mesh) => {
        if (!mesh.userData.reportOriginalMaterial?.color) {
          mesh.material.color.set(cssColor("--rc-text", "#d3d7cf"));
        }
      });
      rebuildOverlays();
      rebuildHelpers();
    };
    window.addEventListener("report-canvas-theme", updateTheme);

    const resize = () => {
      const width = Math.max(stage.clientWidth, 1);
      const height = Math.max(stage.clientHeight, 1);
      renderer.setSize(width, height, false);
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
    };
    const observer = new ResizeObserver(resize);
    observer.observe(stage);
    resize();
    updateTheme();

    let running = true;
    document.addEventListener("visibilitychange", () => {
      running = !document.hidden;
    });
    const animate = () => {
      requestAnimationFrame(animate);
      if (!running) return;
      controls.update();
      try {
        renderer.render(scene, camera);
      } catch (error) {
        running = false;
        stage.replaceChildren(
          create("p", {
            className: "rc-spatial-error",
            text: `3D frame을 렌더링하지 못했습니다: ${error.message}`,
          }),
        );
        console.error(error);
      }
    };
    animate();

    const initialIndex = Math.max(
      0,
      states.findIndex((state) => state.id === visual.initial_state),
    );
    if (stateSelect) stateSelect.value = String(initialIndex);
    setState(initialIndex).catch((error) => {
      stage.replaceChildren(
        create("p", {
          className: "rc-spatial-error",
          text: `3D 데이터를 열지 못했습니다: ${error.message}`,
        }),
      );
    });
  };

  window.ReportCanvasSpatial = { mount };
})();
