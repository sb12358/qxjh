(function () {
  if (!window.React || !window.ReactDOM) {
    return;
  }

  const dataEl = document.getElementById("react-shell-data");
  if (!dataEl) {
    return;
  }

  let shellData = {};
  try {
    shellData = JSON.parse(dataEl.textContent || "{}");
  } catch (_e) {
    shellData = {};
  }

  const e = window.React.createElement;

  function Icon(props) {
    const className = props.className || "";
    if (!className) {
      return null;
    }
    return e("i", { className: className, "aria-hidden": true });
  }

  function Topbar(props) {
    return e(
      "header",
      { className: "topbar" },
      e(
        "div",
        { className: "brand-wrap" },
        e("div", { className: "brand-dot" }),
        e(
          "div",
          null,
          e("div", { className: "brand-title" }, props.brandTitle || "QXJH Data Hub"),
          e("div", { className: "brand-sub" }, props.brandSub || "企业数据整合中台")
        )
      ),
      props.authenticated
        ? e(
            "div",
            { className: "userbox" },
            e(
              "span",
              { className: "badge" },
              e(Icon, { className: "ti ti-user-circle" }),
              props.userDisplay || ""
            ),
            e("a", { className: "text-link", href: props.logoutUrl || "#" }, "退出")
          )
        : null
    );
  }

  function MenuLink(props) {
    const item = props.item;
    const cls = (props.baseClass || "menu-item") + (item.active ? " active" : "");
    const children = [];

    if (item.icon) {
      children.push(e(Icon, { className: item.icon, key: "icon" }));
    }
    children.push(item.label || "");

    return e(
      "a",
      { className: cls, href: item.href || "#", key: item.href || item.label || Math.random() },
      children
    );
  }

  function MenuGroup(props) {
    const item = props.item;
    return e(
      "details",
      { className: "menu-group", open: !!item.open },
      e(
        "summary",
        { className: "menu-item menu-summary" + (item.active ? " active" : "") },
        e(
          "span",
          null,
          item.icon ? e(Icon, { className: item.icon }) : null,
          item.label || ""
        ),
        e("span", { className: "menu-caret", "aria-hidden": true })
      ),
      e(
        "div",
        { className: "submenu" },
        (item.children || []).map(function (child) {
          return e(MenuLink, {
            item: child,
            baseClass: "submenu-item",
            key: child.href || child.label,
          });
        })
      )
    );
  }

  function Sidebar(props) {
    const items = props.items || [];
    return e(
      "aside",
      { className: "sidebar" },
      items.map(function (item) {
        if (item.kind === "group") {
          return e(MenuGroup, { item: item, key: item.label || Math.random() });
        }
        return e(MenuLink, { item: item, baseClass: "menu-item", key: item.href || item.label });
      })
    );
  }

  function mount(rootEl, node) {
    if (!rootEl) {
      return;
    }
    if (window.ReactDOM.createRoot) {
      window.ReactDOM.createRoot(rootEl).render(node);
    } else if (window.ReactDOM.render) {
      window.ReactDOM.render(node, rootEl);
    }
  }

  mount(
    document.getElementById("react-topbar-root"),
    e(Topbar, {
      authenticated: !!shellData.authenticated,
      brandTitle: shellData.brandTitle,
      brandSub: shellData.brandSub,
      userDisplay: shellData.userDisplay,
      logoutUrl: shellData.logoutUrl,
    })
  );

  if (shellData.authenticated) {
    mount(
      document.getElementById("react-sidebar-root"),
      e(Sidebar, {
        items: shellData.navItems || [],
      })
    );
  }
})();
