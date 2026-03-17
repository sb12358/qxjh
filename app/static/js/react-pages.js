(function () {
  if (!window.React || !window.ReactDOM) {
    return;
  }

  var rootEl = document.getElementById("react-page-root");
  var dataEl = document.getElementById("react-page-data");
  if (!rootEl || !dataEl) {
    return;
  }

  var pageData = {};
  try {
    pageData = JSON.parse(dataEl.textContent || "{}");
  } catch (_err) {
    pageData = {};
  }

  var e = window.React.createElement;

  function cx() {
    var classes = [];
    for (var i = 0; i < arguments.length; i += 1) {
      if (arguments[i]) {
        classes.push(arguments[i]);
      }
    }
    return classes.join(" ");
  }

  function Icon(props) {
    if (!props || !props.className) {
      return null;
    }
    return e("i", { className: props.className, "aria-hidden": true });
  }

  function PageHead(props) {
    var actions = props.actions || [];
    return e(
      "section",
      { className: cx("page-head", props.inline ? "page-head-inline" : "") },
      e(
        "div",
        null,
        e("h2", null, props.title || ""),
        props.description ? e("p", null, props.description) : null
      ),
      actions.length
        ? e(
            "div",
            { className: "action-row" },
            actions.map(function (action, idx) {
              return renderAction(action, "head-" + idx);
            })
          )
        : null
    );
  }

  function renderHints(hints) {
    if (!hints || !hints.length) {
      return null;
    }
    return e(
      "div",
      { className: "hint-group" },
      hints.map(function (hint, idx) {
        return e("p", { className: "hint", key: "hint-" + idx }, hint);
      })
    );
  }

  function withConfirm(confirmText) {
    if (!confirmText) {
      return undefined;
    }
    return function (event) {
      if (!window.confirm(confirmText)) {
        event.preventDefault();
      }
    };
  }

  function actionClass(variant) {
    if (variant === "primary") {
      return "btn btn-primary";
    }
    if (variant === "danger") {
      return "btn btn-danger";
    }
    if (variant === "ghost") {
      return "btn btn-ghost";
    }
    return "btn btn-secondary";
  }

  function renderAction(action, key) {
    if (!action) {
      return null;
    }

    var cls = actionClass(action.variant);

    if (action.type === "link") {
      return e(
        "a",
        {
          className: cls,
          href: action.href || "#",
          key: key,
        },
        action.label || ""
      );
    }

    if (action.type === "post") {
      return e(
        "form",
        {
          method: "post",
          action: action.action || "#",
          onSubmit: withConfirm(action.confirm),
          key: key,
        },
        e(
          "button",
          {
            className: cls,
            type: "submit",
            disabled: !!action.disabled,
          },
          action.label || "提交"
        )
      );
    }

    return e(
      "button",
      {
        className: cls,
        type: action.type === "button" ? "button" : "submit",
        key: key,
        disabled: !!action.disabled,
      },
      action.label || "提交"
    );
  }

  function renderCellValue(cell, key) {
    if (cell && typeof cell === "object") {
      if (cell.kind === "badge") {
        return e(
          "span",
          { className: cx("tag", cell.variant ? "tag-" + cell.variant : ""), key: key },
          cell.text || "-"
        );
      }
      if (cell.kind === "actions") {
        var actions = cell.actions || [];
        return e(
          "div",
          { className: "action-row", key: key },
          actions.map(function (action, idx) {
            return renderAction(action, key + "-action-" + idx);
          })
        );
      }
      if (cell.kind === "link") {
        return e(
          "a",
          { href: cell.href || "#", className: "text-link", key: key },
          cell.text || "-"
        );
      }
      return e("span", { key: key }, cell.text || "-");
    }

    if (cell === null || cell === undefined || cell === "") {
      return e("span", { key: key }, "-");
    }

    return e("span", { key: key }, String(cell));
  }

  function DataTable(props) {
    var columns = props.columns || [];
    var rows = props.rows || [];
    var emptyText = props.emptyText || "暂无数据";

    return e(
      "div",
      { className: cx("table-wrap", props.className || "") },
      e(
        "table",
        null,
        e(
          "thead",
          null,
          e(
            "tr",
            null,
            columns.map(function (col, idx) {
              return e("th", { key: "col-" + idx }, col);
            })
          )
        ),
        e(
          "tbody",
          null,
          rows.length
            ? rows.map(function (row, rowIdx) {
                var cells = row.cells || [];
                return e(
                  "tr",
                  { key: "row-" + rowIdx },
                  cells.map(function (cell, cellIdx) {
                    return e("td", { key: "cell-" + rowIdx + "-" + cellIdx }, renderCellValue(cell, "val-" + rowIdx + "-" + cellIdx));
                  })
                );
              })
            : e(
                "tr",
                null,
                e("td", { colSpan: columns.length || 1 }, emptyText)
              )
        )
      )
    );
  }

  function renderField(field, idx) {
    var wrapperClass = cx("field", field.full ? "full" : "");
    var key = "field-" + idx + "-" + (field.name || "anon");

    if (field.type === "checkbox-group") {
      var options = field.options || [];
      return e(
        "div",
        { className: wrapperClass, key: key },
        e("label", null, field.label || ""),
        options.length
          ? e(
              "div",
              { className: "checkbox-grid" },
              options.map(function (option, optionIdx) {
                return e(
                  "label",
                  { className: "checkbox-card", key: key + "-opt-" + optionIdx },
                  e("input", {
                    type: "checkbox",
                    name: field.name,
                    value: option.value,
                    defaultChecked: !!option.checked,
                  }),
                  e("span", null, option.label)
                );
              })
            )
          : e("span", { className: "hint" }, field.emptyText || "暂无可选项")
      );
    }

    if (field.type === "checkbox") {
      return e(
        "div",
        { className: wrapperClass, key: key },
        e(
          "label",
          { className: "checkbox-inline" },
          e("input", {
            type: "checkbox",
            name: field.name,
            defaultChecked: !!field.checked,
          }),
          field.label || ""
        )
      );
    }

    var control = null;
    if (field.type === "select") {
      control = e(
        "select",
        {
          name: field.name,
          required: !!field.required,
          defaultValue: field.value === undefined || field.value === null ? "" : String(field.value),
          disabled: !!field.disabled,
        },
        (field.options || []).map(function (option, optionIdx) {
          return e(
            "option",
            {
              value: option.value,
              key: key + "-select-option-" + optionIdx,
            },
            option.label
          );
        })
      );
    } else if (field.type === "textarea") {
      control = e("textarea", {
        name: field.name,
        required: !!field.required,
        placeholder: field.placeholder || "",
        defaultValue: field.value || "",
        rows: field.rows || 3,
      });
    } else {
      var inputProps = {
        type: field.type || "text",
        name: field.name,
        required: !!field.required,
        placeholder: field.placeholder || "",
        disabled: !!field.disabled,
        minLength: field.minLength || undefined,
        accept: field.accept || undefined,
      };
      if (field.type !== "file") {
        inputProps.defaultValue = field.value || "";
      }
      control = e("input", inputProps);
    }

    return e(
      "div",
      { className: wrapperClass, key: key },
      e("label", null, field.label || ""),
      control
    );
  }

  function FormBlock(props) {
    var form = props.form || {};
    var fields = form.fields || [];
    var actions = form.actions || [];

    return e(
      "form",
      {
        method: form.method || "post",
        action: form.action || "",
        encType: form.encType || undefined,
        className: cx(form.panel === false ? "" : "panel", form.layout === "stack" ? "form-stack" : "form-grid"),
      },
      fields.map(function (field, idx) {
        return renderField(field, idx);
      }),
      actions.length
        ? e(
            "div",
            { className: "action-row" },
            actions.map(function (action, idx) {
              return renderAction(action, "form-action-" + idx);
            })
          )
        : null
    );
  }

  function TablePage(props) {
    return e(
      window.React.Fragment,
      null,
      e(PageHead, {
        title: props.title,
        description: props.description,
        inline: !!props.primaryAction,
        actions: props.primaryAction ? [props.primaryAction] : [],
      }),
      props.createForm ? e(FormBlock, { form: props.createForm }) : null,
      renderHints(props.hints || []),
      props.table ? e(DataTable, { columns: props.table.columns, rows: props.table.rows, emptyText: props.table.emptyText, className: props.table.className }) : null
    );
  }

  function FormPage(props) {
    return e(
      window.React.Fragment,
      null,
      e(PageHead, {
        title: props.title,
        description: props.description,
      }),
      e(FormBlock, { form: props.form }),
      renderHints(props.hints || [])
    );
  }

  function LoginPage(props) {
    return e(
      "div",
      { className: "login-single" },
      e(
        "section",
        { className: "login-card" },
        e("h2", null, props.title || "账号登录"),
        e(FormBlock, {
          form: {
            method: "post",
            action: props.action || "",
            panel: false,
            layout: "stack",
            fields: props.fields || [],
            actions: props.actions || [],
          },
        }),
        props.hint ? e("p", { className: "hint" }, props.hint) : null
      )
    );
  }

  function OverviewPage(props) {
    var metrics = props.metrics || [];
    return e(
      window.React.Fragment,
      null,
      e(PageHead, {
        title: props.title,
        description: props.description,
      }),
      metrics.length
        ? e(
            "div",
            { className: "metric-grid" },
            metrics.map(function (metric, idx) {
              return e(
                "article",
                { className: "metric-card", key: "metric-" + idx },
                e("span", null, metric.label || ""),
                e("strong", null, metric.value || "0")
              );
            })
          )
        : null,
      props.recommendActions && props.recommendActions.length
        ? e(
            "div",
            { className: "panel-grid" },
            e(
              "section",
              { className: "panel" },
              e("h3", null, props.recommendTitle || "推荐操作"),
              e(
                "div",
                { className: "action-row" },
                props.recommendActions.map(function (action, idx) {
                  return renderAction(action, "recommend-" + idx);
                })
              )
            )
          )
        : null
    );
  }

  function SettlementFundPage(props) {
    return e(
      window.React.Fragment,
      null,
      e(PageHead, {
        title: props.title,
        description: props.description,
      }),
      e(FormBlock, { form: props.uploadForm }),
      e(
        "div",
        { className: "panel" },
        e("h3", { className: "panel-title" }, "按结算日期查看"),
        e(FormBlock, { form: Object.assign({}, props.filterForm, { panel: false }) }),
        e(
          "div",
          { className: "action-row" },
          (props.quickDates || []).length
            ? (props.quickDates || []).map(function (item, idx) {
                return renderAction(
                  {
                    type: "link",
                    href: item.href,
                    label: item.label,
                    variant: item.active ? "primary" : "secondary",
                  },
                  "quick-date-" + idx
                );
              })
            : e("span", { className: "hint" }, "暂无可选结算日期")
        )
      ),
      props.currentDateText ? e("p", { className: "hint" }, props.currentDateText) : null,
      props.table && props.table.columns && props.table.columns.length
        ? e(DataTable, {
            columns: props.table.columns,
            rows: props.table.rows,
            emptyText: props.table.emptyText,
            className: "settlement-table-wrap",
          })
        : e("p", { className: "hint" }, props.emptyText || "暂无数据")
    );
  }

  function renderPage(data) {
    if (!data || !data.type) {
      return e("div", { className: "panel" }, e("p", { className: "hint" }, "页面配置缺失"));
    }

    if (data.type === "login") {
      return e(LoginPage, data);
    }
    if (data.type === "overview") {
      return e(OverviewPage, data);
    }
    if (data.type === "form") {
      return e(FormPage, data);
    }
    if (data.type === "settlement-fund") {
      return e(SettlementFundPage, data);
    }
    return e(TablePage, data);
  }

  if (window.ReactDOM.createRoot) {
    window.ReactDOM.createRoot(rootEl).render(renderPage(pageData));
  } else {
    window.ReactDOM.render(renderPage(pageData), rootEl);
  }
})();
