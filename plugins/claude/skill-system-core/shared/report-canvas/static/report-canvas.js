(() => {
  "use strict";

  const root = document.getElementById("report-canvas");
  const dataNode = document.getElementById("report-data");

  const create = (tag, options = {}) => {
    const node = document.createElement(tag);
    if (options.className) node.className = options.className;
    if (options.text !== undefined) node.textContent = String(options.text);
    if (options.attrs) {
      Object.entries(options.attrs).forEach(([name, value]) => {
        if (value !== undefined && value !== null) {
          node.setAttribute(name, String(value));
        }
      });
    }
    return node;
  };

  const append = (parent, ...children) => {
    children.filter(Boolean).forEach((child) => parent.appendChild(child));
    return parent;
  };

  const safeHref = (value) => {
    if (typeof value !== "string" || !value.trim()) return null;
    if (value.startsWith("#")) return value;
    try {
      const url = new URL(value);
      return ["https:", "http:"].includes(url.protocol) ? url.href : null;
    } catch {
      return null;
    }
  };

  const label = (value) => String(value || "").replaceAll("_", " ");

  const makeChip = (text, tone = "info", extraClass = "") =>
    create("span", {
      className: `rc-chip ${extraClass}`.trim(),
      text,
      attrs: { "data-tone": tone },
    });

  let model;
  try {
    model = JSON.parse(dataNode.textContent);
  } catch (error) {
    root.appendChild(
      create("p", {
        className: "rc-spatial-error",
        text: `Report model을 읽지 못했습니다: ${error.message}`,
      }),
    );
    return;
  }

  document.title = model.title;

  const evidenceById = new Map(
    (model.evidence || []).map((item) => [item.id, item]),
  );
  const evidenceNodes = new Map();

  const themeLabels = {
    auto: "System · Oblivion",
    dark: "Oblivion",
    light: "Oblivion Hagoromo",
  };
  const themeOrder = ["auto", "dark", "light"];
  const readSavedTheme = () => {
    try {
      return localStorage.getItem("skill-system-report-theme");
    } catch {
      return null;
    }
  };
  const saveTheme = (theme) => {
    try {
      localStorage.setItem("skill-system-report-theme", theme);
    } catch {
      // A file:// origin may deny storage. The in-document toggle still works.
    }
  };
  const savedTheme = readSavedTheme();
  const initialTheme = themeOrder.includes(savedTheme) ? savedTheme : "auto";
  document.documentElement.dataset.theme = initialTheme;

  const themeButton = create("button", {
    className: "rc-theme-toggle",
    attrs: { type: "button", "aria-label": "색상 테마 변경" },
  });
  const themeSwatch = create("span", {
    className: "rc-theme-swatch",
    attrs: { "aria-hidden": "true" },
  });
  const themeText = create("span", { text: themeLabels[initialTheme] });
  append(themeButton, themeSwatch, themeText);
  themeButton.addEventListener("click", () => {
    const current = document.documentElement.dataset.theme || "auto";
    const next = themeOrder[(themeOrder.indexOf(current) + 1) % themeOrder.length];
    document.documentElement.dataset.theme = next;
    themeText.textContent = themeLabels[next];
    saveTheme(next);
    window.dispatchEvent(new CustomEvent("report-canvas-theme"));
  });

  const firstView = create("section", { className: "rc-first-view" });
  const topbar = create("header", { className: "rc-topbar" });
  const heading = create("div", { className: "rc-heading" });
  const eyebrow = typeof model.eyebrow === "string" ? model.eyebrow.trim() : "";
  if (eyebrow) {
    heading.appendChild(create("p", { className: "rc-kicker", text: eyebrow }));
  }
  append(
    heading,
    create("h1", { className: "rc-title", text: model.title }),
    create("p", { className: "rc-summary", text: model.summary }),
  );
  append(topbar, heading, themeButton);

  const meta = create("div", { className: "rc-meta-row" });
  append(
    meta,
    makeChip(label(model.status), model.status),
    makeChip(label(model.evidence_status), model.evidence_status),
    makeChip(model.mode, "info"),
  );
  if (model.snapshot?.label) {
    const snapshotText = model.snapshot.ref
      ? `${model.snapshot.label} · ${model.snapshot.ref}`
      : model.snapshot.label;
    meta.appendChild(makeChip(snapshotText, "info", "rc-snapshot"));
  }

  const mainGrid = create("div", { className: "rc-main-grid" });
  const visualPanel = create("section", {
    className: "rc-panel rc-visual-panel",
  });
  const visualHead = create("header", { className: "rc-panel-head" });
  append(
    visualHead,
    create("h2", { text: "Core view" }),
    create("span", { className: "rc-mode", text: model.mode }),
  );
  const visualBody = create("div", { className: "rc-visual-body" });
  append(visualPanel, visualHead, visualBody);

  const findingsPanel = create("aside", {
    className: "rc-panel rc-findings",
  });
  findingsPanel.appendChild(create("h2", { text: "Top findings" }));
  const findingsList = create("div", { className: "rc-findings-list" });
  const findings = model.findings || [];
  if (!findings.length) {
    findingsList.appendChild(
      create("p", {
        className: "rc-empty",
        text: "이 첫 화면에 올릴 material finding은 없습니다.",
      }),
    );
  }

  const openEvidence = (id) => {
    const node = evidenceNodes.get(id);
    if (!node) return;
    node.open = true;
    node.scrollIntoView({ behavior: "smooth", block: "center" });
    node.focus({ preventScroll: true });
  };

  findings.slice(0, 3).forEach((finding) => {
    const card = create("article", {
      className: "rc-finding",
      attrs: { "data-severity": finding.severity || "info" },
    });
    append(
      card,
      makeChip(label(finding.severity || "info"), finding.severity || "info"),
      create("h3", { className: "rc-finding-title", text: finding.title }),
      create("p", {
        className: "rc-finding-summary",
        text: finding.summary,
      }),
    );
    if (Array.isArray(finding.evidence_refs) && finding.evidence_refs.length) {
      const refs = create("div", { className: "rc-chip-row" });
      finding.evidence_refs.forEach((id) => {
        const button = create("button", {
          className: "rc-evidence-ref",
          text: evidenceById.has(id) ? `#${id}` : `#${id} · missing`,
          attrs: { type: "button" },
        });
        button.addEventListener("click", () => openEvidence(id));
        refs.appendChild(button);
      });
      card.appendChild(refs);
    }
    findingsList.appendChild(card);
  });
  findingsPanel.appendChild(findingsList);
  append(mainGrid, visualPanel, findingsPanel);

  const actionKind = model.next_action.kind === "none" ? "none" : "next";
  const nextAction = create("section", {
    className: "rc-next-action",
    attrs: { "data-action-kind": actionKind },
  });
  const nextIndex = create("span", {
    className: "rc-next-index",
    text: actionKind === "none" ? "—" : "→",
  });
  const nextCopy = create("div", { className: "rc-next-copy" });
  append(
    nextCopy,
    create("strong", { text: model.next_action.label }),
    model.next_action.detail
      ? create("span", { text: model.next_action.detail })
      : null,
  );
  append(nextAction, nextIndex, nextCopy);
  const actionHref =
    actionKind === "next" ? safeHref(model.next_action.href) : null;
  if (actionHref) {
    nextAction.appendChild(
      create("a", {
        className: "rc-next-link",
        text: "Open ↗",
        attrs: {
          href: actionHref,
          target: actionHref.startsWith("#") ? "_self" : "_blank",
          rel: "noreferrer",
        },
      }),
    );
  }

  append(firstView, topbar, meta, mainGrid, nextAction);
  root.appendChild(firstView);

  const renderDecision = (visual) => {
    const wrap = create("div", { className: "rc-decision" });
    wrap.appendChild(
      create("p", { className: "rc-decision-prompt", text: visual.prompt }),
    );
    const grid = create("div", { className: "rc-choice-grid" });
    (visual.choices || []).forEach((choice) => {
      const button = create("button", {
        className: "rc-choice",
        attrs: {
          type: "button",
          "aria-pressed": "false",
          "data-choice": choice.id,
        },
      });
      append(
        button,
        choice.recommended
          ? create("span", { className: "rc-choice-tag", text: "RECOMMENDED" })
          : null,
        create("strong", { text: choice.label }),
        create("span", { text: choice.description }),
        choice.consequence
          ? create("small", { text: choice.consequence })
          : null,
      );
      button.addEventListener("click", () => {
        grid
          .querySelectorAll(".rc-choice")
          .forEach((item) => item.setAttribute("aria-pressed", "false"));
        button.setAttribute("aria-pressed", "true");
      });
      grid.appendChild(button);
    });
    append(wrap, grid);
    visualBody.appendChild(wrap);
  };

  const contentBlock = (block) => {
    const article = create("article", { className: "rc-content-block" });
    const header = create("header");
    append(
      header,
      create("strong", { text: block.label }),
      block.status ? create("span", { text: label(block.status) }) : null,
    );
    const pre = create("pre");
    const code = create("code", {
      text: block.content,
      attrs: block.language ? { "data-language": block.language } : {},
    });
    pre.appendChild(code);
    append(article, header, pre);
    return article;
  };

  const renderCompare = (visual) => {
    const compare = create("div", { className: "rc-compare" });
    [
      [visual.before_label || "Before", visual.before || []],
      [visual.after_label || "After", visual.after || []],
    ].forEach(([columnLabel, blocks]) => {
      const column = create("section", { className: "rc-compare-column" });
      column.appendChild(create("h3", { text: columnLabel }));
      blocks.forEach((block) => column.appendChild(contentBlock(block)));
      compare.appendChild(column);
    });
    visualBody.appendChild(compare);
  };

  const renderTrace = (visual) => {
    const trace = create("div", { className: "rc-trace" });
    const outgoing = new Map();
    (visual.edges || []).forEach((edge) => {
      if (!outgoing.has(edge.from)) outgoing.set(edge.from, []);
      outgoing.get(edge.from).push(edge);
    });
    (visual.nodes || []).forEach((node) => {
      const card = create("article", { className: "rc-trace-node" });
      const evidenceStatus = node.status || "unverified";
      const statusChips = create("div", { className: "rc-chip-row" });
      statusChips.appendChild(
        makeChip(`evidence · ${label(evidenceStatus)}`, evidenceStatus),
      );
      if (node.lifecycle_status) {
        statusChips.appendChild(
          makeChip(
            `lifecycle · ${label(node.lifecycle_status)}`,
            node.lifecycle_status,
          ),
        );
      }
      append(
        card,
        statusChips,
        create("h3", { text: node.label }),
        node.detail ? create("p", { text: node.detail }) : null,
      );
      const edges = outgoing.get(node.id) || [];
      if (edges.length) {
        card.appendChild(
          create("div", {
            className: "rc-trace-edge",
            text: edges
              .map((edge) => `${edge.label || "next"} → ${edge.to}`)
              .join(" · "),
          }),
        );
      }
      (node.evidence_refs || []).forEach((id) => {
        const button = create("button", {
          className: "rc-evidence-ref",
          text: `#${id}`,
          attrs: { type: "button" },
        });
        button.addEventListener("click", () => openEvidence(id));
        card.appendChild(button);
      });
      trace.appendChild(card);
    });
    visualBody.appendChild(trace);
  };

  const renderSpatial = (visual) => {
    if (!window.ReportCanvasSpatial?.mount) {
      visualBody.appendChild(
        create("p", {
          className: "rc-spatial-error",
          text: "Spatial runtime이 이 산출물에 포함되지 않았습니다.",
        }),
      );
      return;
    }
    window.ReportCanvasSpatial.mount(visualBody, visual, {
      onEvidence: openEvidence,
    });
  };

  const visual = model.visual;
  if (!visual) {
    visualBody.appendChild(
      create("p", {
        className: "rc-empty",
        text: "핵심 시각 모델이 없습니다. 결론과 근거만 표시합니다.",
      }),
    );
  } else if (visual.type === "decision") {
    renderDecision(visual);
  } else if (visual.type === "compare") {
    renderCompare(visual);
  } else if (visual.type === "trace") {
    renderTrace(visual);
  } else if (visual.type === "spatial") {
    renderSpatial(visual);
  }

  const evidenceSection = create("section", {
    className: "rc-evidence-section",
    attrs: { id: "evidence" },
  });
  append(
    evidenceSection,
    create("h2", { text: "Evidence drawers" }),
    create("p", {
      className: "rc-evidence-intro",
      text: "이 Canvas는 탐색용 파생 뷰입니다. 판단에 쓰이는 원본 source, runtime, test, diff anchor는 아래에서 다시 확인하세요.",
    }),
  );
  const evidenceList = create("div", { className: "rc-evidence-list" });
  (model.evidence || []).forEach((item) => {
    const details = create("details", {
      className: "rc-evidence",
      attrs: { id: `evidence-${item.id}`, tabindex: "-1" },
    });
    const summary = create("summary");
    append(
      summary,
      create("span", { className: "rc-evidence-title", text: item.title }),
      makeChip(`${label(item.kind)} · ${label(item.status)}`, item.status),
    );
    const body = create("div", { className: "rc-evidence-body" });
    append(
      body,
      item.summary ? create("p", { text: item.summary }) : null,
      create("span", { className: "rc-source", text: item.source }),
    );
    if (item.details) {
      const pre = create("pre");
      pre.appendChild(create("code", { text: item.details }));
      body.appendChild(pre);
    }
    const href = safeHref(item.href);
    if (href) {
      body.appendChild(
        create("a", {
          className: "rc-next-link",
          text: "원본 링크 열기 ↗",
          attrs: { href, target: "_blank", rel: "noreferrer" },
        }),
      );
    }
    append(details, summary, body);
    evidenceNodes.set(item.id, details);
    evidenceList.appendChild(details);
  });
  evidenceSection.appendChild(evidenceList);

  if (Array.isArray(model.participation) && model.participation.length) {
    const participation = create("div", { className: "rc-participation" });
    model.participation.forEach((item) => {
      participation.appendChild(
        makeChip(`${label(item.kind)} · ${label(item.status)}`, item.status),
      );
    });
    evidenceSection.appendChild(participation);
  }
  root.appendChild(evidenceSection);
})();
