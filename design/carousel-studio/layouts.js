/* Carousel Studio layouts.
   One file used by both the builder (headless Chrome) and the browser editor, so what you see while
   editing is exactly what gets exported.

   Slide fields (every layout reads from the same set, so switching layouts keeps the words):
     kicker, headline, body, sub, items[], number, left_label, left, right_label, right, cta,
     photo {src, x, y, zoom}, photo2 {src, x, y, zoom}
   Wrap a word in **double stars** to highlight it in the accent color. */
(function (root) {
  "use strict";

  var PH = {
    kicker: "Small label", headline: "Headline", body: "A line or two of body text", sub: "Small line",
    items: "List item", number: "40%", left_label: "Before", left: "How it was", right_label: "After",
    right: "How it is now", cta: "WORD"
  };

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (m) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[m];
    });
  }
  function rich(s) {
    return esc(s).replace(/\*\*(.+?)\*\*/g, '<span class="hl">$1</span>').replace(/\n/g, "<br>");
  }
  function plain(s) { return String(s == null ? "" : s).replace(/\*\*/g, ""); }
  function get(s, path) {
    var p = path.split(".");
    var v = s[p[0]];
    if (p.length > 1) v = (v || [])[+p[1]];
    return v;
  }

  /* ---------- small builders shared by the layouts ---------- */
  function kit(s, c) {
    var k = {};
    k.t = function (f, cls, tag) {
      tag = tag || "div";
      var v = get(s, f);
      var empty = v == null || v === "";
      if (empty && !c.edit) return "";
      return "<" + tag + ' class="' + (cls || "") + (empty ? " is-empty" : "") + '" data-field="' + f +
        '" data-ph="' + esc(PH[f.split(".")[0]] || f) + '">' + (empty ? "" : rich(v)) + "</" + tag + ">";
    };
    k.has = function (f) { var v = get(s, f); return !(v == null || v === "" || (Array.isArray(v) && !v.length)); };
    k.items = function (max) {
      var arr = (s.items || []).slice(0, max || 8);
      var idx = arr.map(function (_, i) { return i; });
      if (!c.edit) idx = idx.filter(function (i) { return String(arr[i] || "").trim(); });
      if (c.edit && !idx.length) idx = [0];
      return idx;
    };
    k.photo = function (key, cls) {
      key = key || "photo";
      var p = s[key];
      var src = p && (typeof p === "string" ? p : p.src);
      var o = (p && typeof p === "object") ? p : {};
      var x = o.x == null ? 50 : o.x, y = o.y == null ? 50 : o.y, z = o.zoom || 1;
      var inner = src
        ? '<img src="' + esc(c.photoUrl(src)) + '" draggable="false" style="object-position:' + x + "% " + y +
          "%;transform:scale(" + z + ");transform-origin:" + x + "% " + y + '%">'
        : (c.edit ? '<div class="ph-empty"><span>Click to add a photo</span></div>' : '<div class="ph-soft"></div>');
      return '<div class="ph ' + (cls || "") + '" data-photo="' + key + '">' + inner + "</div>";
    };
    k.hasPhoto = function (key) { var p = s[key || "photo"]; return !!(p && (typeof p === "string" ? p : p.src)); };
    k.box = function (cls, inner) { return '<div class="fitbox ' + (cls || "") + '"><div class="fi">' + inner + "</div></div>"; };
    return k;
  }

  var SVG = {
    arrow: '<svg viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
    check: '<svg viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>',
    cross: '<svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18"/></svg>',
    down: '<svg viewBox="0 0 24 24"><path d="M12 5v14M6 13l6 6 6-6"/></svg>',
    heart: '<svg viewBox="0 0 24 24"><path d="M12 20s-7-4.4-9.2-8.6C1.2 8.2 3 4.5 6.6 4.5c2.1 0 3.6 1.2 5.4 3.2 1.8-2 3.3-3.2 5.4-3.2 3.6 0 5.4 3.7 3.8 6.9C19 15.6 12 20 12 20z"/></svg>',
    chat: '<svg viewBox="0 0 24 24"><path d="M4 5h16v11H9l-5 4z"/></svg>',
    send: '<svg viewBox="0 0 24 24"><path d="M21 3L10 14M21 3l-7 18-4-7-7-4z"/></svg>',
    save: '<svg viewBox="0 0 24 24"><path d="M6 3h12v18l-6-5-6 5z"/></svg>',
    bookmark: '<svg viewBox="0 0 100 130"><path d="M8 0h84a8 8 0 0 1 8 8v122L50 100 0 130V8a8 8 0 0 1 8-8z"/></svg>'
  };

  function pct(n) {
    var m = String(n || "").match(/(\d+(?:\.\d+)?)\s*%/);
    if (m) return Math.max(0, Math.min(100, parseFloat(m[1])));
    var f = String(n || "").match(/(\d+)\s*(?:\/|of|out of)\s*(\d+)/i);
    if (f) return Math.max(0, Math.min(100, 100 * f[1] / f[2]));
    return 75;
  }
  function initial(c) { return esc((plain(c.name || c.handle || "?").replace(/^@/, "")[0] || "?").toUpperCase()); }

  /* ---------- the layouts ---------- */
  var L = [];
  function add(def) { L.push(def); }

  // PHOTO-LED
  add({ id: "photo-full", name: "Full photo", group: "Photo-led", roles: ["cover", "point", "close"], photos: 1, tone: "on-dark", light: true,
    fields: ["kicker", "headline", "body", "photo"],
    html: function (s, c, k) {
      return k.photo() + '<div class="scrim"></div>' + k.box("", k.t("kicker", "K") + k.t("headline", "H") + k.t("body", "B"));
    } });

  add({ id: "photo-frame", name: "Framed photo", group: "Photo-led", roles: ["cover", "point"], photos: 1,
    fields: ["kicker", "headline", "body", "photo"],
    html: function (s, c, k) {
      return '<div class="frame"></div>' + k.photo() + k.box("", k.t("kicker", "K") + k.t("headline", "H") + k.t("body", "B"));
    } });

  add({ id: "photo-top", name: "Photo on top", group: "Photo-led", roles: ["point", "cover"], photos: 1,
    fields: ["kicker", "headline", "body", "photo"],
    html: function (s, c, k) {
      return k.photo() + '<div class="panel"></div>' +
        (k.has("kicker") || c.edit ? '<div class="tab">' + k.t("kicker", "pill") + "</div>" : "") +
        k.box("", k.t("headline", "H") + k.t("body", "B"));
    } });

  add({ id: "photo-arch", name: "Arch window", group: "Photo-led", roles: ["cover", "point", "close"], photos: 1,
    fields: ["kicker", "headline", "body", "photo"],
    html: function (s, c, k) {
      return '<div class="arch-line"></div>' + k.photo() + k.box("", k.t("kicker", "K") + k.t("headline", "H") + k.t("body", "B"));
    } });

  add({ id: "polaroid", name: "Polaroid", group: "Photo-led", roles: ["cover", "point"], photos: 1,
    fields: ["kicker", "headline", "body", "photo"],
    html: function (s, c, k) {
      return '<div class="card"><div class="tape"></div>' + k.photo() + '<div class="cap">' + k.t("kicker", "S") + "</div></div>" +
        k.box("", k.t("headline", "H") + k.t("body", "B"));
    } });

  add({ id: "photo-window", name: "Photo + card", group: "Photo-led", roles: ["point", "cover"], photos: 1,
    fields: ["kicker", "headline", "body", "photo"],
    html: function (s, c, k) {
      return k.photo() + k.box("", k.t("kicker", "K") + k.t("headline", "H") + k.t("body", "B"));
    } });

  add({ id: "cover-magazine", name: "Magazine cover", group: "Photo-led", roles: ["cover"], photos: 1, tone: "on-dark", light: true,
    fields: ["kicker", "headline", "body", "photo"],
    html: function (s, c, k) {
      return k.photo() + '<div class="scrim"></div>' +
        '<div class="mast"><div class="H" data-fitw="1">' + esc(c.name || "Your Name") + '</div><div class="issue"><span>' +
        esc(c.handle || "") + "</span><span>" + (c.n ? "1 of " + c.n : "") + "</span></div></div>" +
        k.box("", k.t("kicker", "K") + k.t("headline", "H head") + k.t("body", "B"));
    } });

  // TYPE-LED
  add({ id: "big-type", name: "Big type", group: "Type-led", roles: ["cover", "point"], photos: 0,
    fields: ["kicker", "headline", "body"],
    html: function (s, c, k) {
      return k.box("", k.t("kicker", "K") + k.t("headline", "H") + '<div class="rule"></div>' + k.t("body", "B"));
    } });

  add({ id: "color-block", name: "Color block", group: "Type-led", roles: ["cover", "point", "close"], photos: 0, tone: "on-accent",
    fields: ["kicker", "headline", "body"],
    html: function (s, c, k) {
      return '<div class="blob"></div><div class="blob2"></div>' + k.box("", k.t("kicker", "K") + k.t("headline", "H") + k.t("body", "B"));
    } });

  add({ id: "editorial", name: "Editorial page", group: "Type-led", roles: ["point"], photos: 0,
    fields: ["kicker", "headline", "body"],
    html: function (s, c, k) {
      var long = plain(s.body).length > 150;
      var kv = String(s.kicker || "").trim();
      var hide = kv === "-";
      var isNum = /^\d{1,2}$/.test(kv);
      var numKicker = !c.edit && (isNum || hide);
      var big = isNum ? kv.padStart(2, "0") : String(c.i + 1).padStart(2, "0");
      var kt = k.t("kicker", "K").replace(/data-ph="[^"]*"/, 'data-ph="Number, or - to hide it"');
      return '<div class="mast"><span>' + esc(c.name || "") + "</span><span>" + esc(c.handle || "") + '</span></div><div class="mast2"></div>' +
        (hide ? "" : '<div class="idx">' + esc(big) + "</div>") +
        k.box(hide ? "up" : "", (numKicker ? "" : kt) + k.t("headline", "H") + k.t("body", "B" + (long ? "" : " one")));
    } });

  add({ id: "outline-word", name: "Outline word", group: "Type-led", roles: ["cover", "point"], photos: 0, tone: "on-dark",
    fields: ["kicker", "headline", "body"],
    html: function (s, c, k) { return k.box("", k.t("kicker", "K") + k.t("headline", "H") + k.t("body", "B")); } });

  add({ id: "note-card", name: "Note card", group: "Type-led", roles: ["point", "quote"], photos: 0,
    fields: ["kicker", "headline", "body"],
    html: function (s, c, k) {
      return '<div class="card"><div class="tape"></div></div>' + k.box("", k.t("kicker", "K") + k.t("headline", "H") + k.t("body", "B"));
    } });

  add({ id: "question", name: "Big question", group: "Type-led", roles: ["cover", "point"], photos: 0,
    fields: ["kicker", "headline", "body"],
    html: function (s, c, k) { return '<div class="qmark">?</div>' + k.box("", k.t("kicker", "K") + k.t("headline", "H") + k.t("body", "B")); } });

  add({ id: "definition", name: "Definition", group: "Type-led", roles: ["cover", "point"], photos: 0,
    fields: ["headline", "kicker", "body", "sub"],
    html: function (s, c, k) {
      return k.box("", k.t("headline", "H") + k.t("kicker", "K") + '<div class="rule"></div>' +
        '<div class="num"><b>1.</b>' + k.t("body", "B") + "</div>" + k.t("sub", "B ex muted"));
    } });

  add({ id: "cover-sticker", name: "Sticker cover", group: "Type-led", roles: ["cover"], photos: 0,
    fields: ["kicker", "headline", "body", "cta"],
    html: function (s, c, k) {
      return k.box("", (k.has("kicker") || c.edit ? '<div>' + k.t("kicker", "stk", "span") + "</div>" : "") + k.t("headline", "H") + k.t("body", "B")) +
        '<div class="badge">' + (k.has("cta") || c.edit ? k.t("cta", "", "span") : "Swipe") + "</div>";
    } });

  // QUOTE
  add({ id: "quote-classic", name: "Classic quote", group: "Quote", roles: ["quote"], photos: 0,
    fields: ["headline", "sub"],
    html: function (s, c, k) {
      return '<div class="mark">“</div>' + k.box("", k.t("headline", "H Q") + k.t("sub", "by"));
    } });

  add({ id: "quote-photo", name: "Quote on photo", group: "Quote", roles: ["quote", "cover"], photos: 1, tone: "on-dark", light: true,
    fields: ["kicker", "headline", "sub", "photo"],
    html: function (s, c, k) {
      return k.photo() + '<div class="scrim"></div>' + k.box("", k.t("kicker", "K") + k.t("headline", "H Q") + k.t("sub", "by"));
    } });

  add({ id: "quote-post", name: "Post card", group: "Quote", roles: ["quote", "point"], photos: 1,
    fields: ["headline", "photo"],
    html: function (s, c, k) {
      return '<div class="card"><div class="who"><div class="av">' + (k.hasPhoto() ? k.photo() : (c.edit ? k.photo() : initial(c))) +
        '</div><div><div class="nm">' + esc(c.name || "Your Name") + '</div><div class="hd">' + esc(c.handle || "") + "</div></div></div>" +
        k.box("", k.t("headline", "H")) +
        '<div class="icons">' + SVG.heart + SVG.chat + SVG.send + '<span style="flex:1"></span>' + SVG.save + "</div></div>";
    } });

  add({ id: "quote-verse", name: "Verse frame", group: "Quote", roles: ["quote"], photos: 0,
    fields: ["kicker", "headline", "sub"],
    html: function (s, c, k) {
      return '<div class="frame"></div><div class="frame2"></div><div class="orn"></div><div class="orn2"></div>' +
        k.box("", k.t("kicker", "K") + k.t("headline", "H Q") + k.t("sub", "by"));
    } });

  // NUMBER / STAT
  add({ id: "stat-giant", name: "Giant number", group: "Number", roles: ["stat"], photos: 0,
    fields: ["kicker", "number", "headline", "body"],
    html: function (s, c, k) {
      return k.box("", k.t("kicker", "K") + k.t("number", "num") + k.t("headline", "H") + k.t("body", "B"));
    } });

  add({ id: "stat-ring", name: "Progress ring", group: "Number", roles: ["stat"], photos: 0, tone: "on-dark",
    fields: ["number", "headline", "body"],
    html: function (s, c, k) {
      var p = pct(s.number), r = 270, C = 2 * Math.PI * r;
      return '<div class="ring"><svg viewBox="0 0 620 620"><circle cx="310" cy="310" r="' + r + '" fill="none" stroke="currentColor" stroke-opacity=".14" stroke-width="44"/>' +
        '<circle cx="310" cy="310" r="' + r + '" fill="none" stroke="var(--accent)" stroke-width="44" stroke-linecap="round" stroke-dasharray="' +
        (C * p / 100).toFixed(1) + " " + C.toFixed(1) + '"/></svg>' + k.t("number", "num") + "</div>" +
        k.box("", k.t("headline", "H") + k.t("body", "B"));
    } });

  add({ id: "stat-split", name: "Number + photo", group: "Number", roles: ["stat"], photos: 1,
    fields: ["kicker", "number", "headline", "body", "photo"],
    html: function (s, c, k) {
      return k.photo() + k.box("", k.t("kicker", "K") + k.t("number", "num") + k.t("headline", "H") + k.t("body", "B"));
    } });

  // LIST / STEPS
  add({ id: "list-numbered", name: "Numbered list", group: "List & steps", roles: ["list"], photos: 0,
    fields: ["kicker", "headline", "items"],
    html: function (s, c, k) {
      var li = k.items(7).map(function (i) { return "<li><b>" + String(i + 1).padStart(2, "0") + "</b>" + k.t("items." + i, "B") + "</li>"; }).join("");
      return k.box("", k.t("kicker", "K") + k.t("headline", "H") + "<ol>" + li + "</ol>");
    } });

  add({ id: "steps-timeline", name: "Step timeline", group: "List & steps", roles: ["list"], photos: 0,
    fields: ["kicker", "headline", "items"],
    html: function (s, c, k) {
      var st = k.items(6).map(function (i) { return '<div class="st"><div class="dot">' + (i + 1) + "</div>" + k.t("items." + i, "B") + "</div>"; }).join("");
      return k.box("", k.t("kicker", "K") + k.t("headline", "H") + '<div class="tl">' + st + "</div>");
    } });

  add({ id: "checklist", name: "Checklist", group: "List & steps", roles: ["list"], photos: 0,
    fields: ["kicker", "headline", "items"],
    html: function (s, c, k) {
      var r = k.items(6).map(function (i) { return '<div class="row"><div class="box">' + SVG.check + "</div>" + k.t("items." + i, "B") + "</div>"; }).join("");
      return k.box("", k.t("kicker", "K") + k.t("headline", "H") + '<div class="ck">' + r + "</div>");
    } });

  add({ id: "grid-four", name: "Four tiles", group: "List & steps", roles: ["list"], photos: 0,
    fields: ["kicker", "headline", "items"],
    html: function (s, c, k) {
      var t = k.items(6).map(function (i) { return '<div class="tile"><b>' + (i + 1) + "</b>" + k.t("items." + i, "B") + "</div>"; }).join("");
      return k.box("", k.t("kicker", "K") + k.t("headline", "H") + '<div class="grid">' + t + "</div>");
    } });

  add({ id: "list-photo", name: "List + photo", group: "List & steps", roles: ["list"], photos: 1,
    fields: ["kicker", "headline", "items", "photo"],
    html: function (s, c, k) {
      var li = k.items(6).map(function (i) { return "<li>" + k.t("items." + i, "B") + "</li>"; }).join("");
      return k.photo() + k.box("", k.t("kicker", "K") + k.t("headline", "H") + "<ul>" + li + "</ul>");
    } });

  // SPLIT / COMPARE
  add({ id: "split-photo", name: "Half photo", group: "Split & compare", roles: ["point", "cover"], photos: 1,
    fields: ["kicker", "headline", "body", "photo"],
    html: function (s, c, k) { return k.photo() + k.box("", k.t("kicker", "K") + k.t("headline", "H") + k.t("body", "B")); } });

  add({ id: "split-diagonal", name: "Diagonal split", group: "Split & compare", roles: ["cover", "point"], photos: 1,
    fields: ["kicker", "headline", "body", "photo"],
    html: function (s, c, k) {
      return '<div class="band"></div>' + k.photo() + k.box("", k.t("kicker", "K") + k.t("headline", "H") + k.t("body", "B"));
    } });

  add({ id: "before-after", name: "Before / after", group: "Split & compare", roles: ["compare"], photos: 2,
    fields: ["left_label", "left", "photo", "right_label", "right", "photo2"],
    html: function (s, c, k) {
      function half(cls, lab, txt, key, deflab) {
        var hp = k.hasPhoto(key);
        return '<div class="half ' + cls + (hp ? " has-photo" : "") + '">' + (hp || c.edit ? k.photo(key) : "") +
          (hp ? '<div class="scrim"></div>' : "") +
          '<div class="tag">' + (k.has(lab) || c.edit ? k.t(lab, "", "span") : deflab) + "</div>" +
          k.box("", k.t(txt, "H")) + "</div>";
      }
      return half("a", "left_label", "left", "photo", "Before") + half("b", "right_label", "right", "photo2", "After") +
        '<div class="mid">' + SVG.down + "</div>";
    } });

  add({ id: "myth-truth", name: "Myth vs truth", group: "Split & compare", roles: ["compare"], photos: 0,
    fields: ["headline", "left_label", "left", "right_label", "right"],
    html: function (s, c, k) {
      return k.box("", k.t("headline", "H top") +
        '<div class="cd m"><div class="lb">' + SVG.cross + (k.has("left_label") || c.edit ? k.t("left_label", "", "span") : "Myth") + "</div>" + k.t("left", "tx") + "</div>" +
        '<div class="cd t"><div class="lb">' + SVG.check + (k.has("right_label") || c.edit ? k.t("right_label", "", "span") : "Truth") + "</div>" + k.t("right", "tx") + "</div>");
    } });

  add({ id: "side-by-side", name: "This, not that", group: "Split & compare", roles: ["compare"], photos: 0,
    fields: ["headline", "left_label", "left", "right_label", "right"],
    html: function (s, c, k) {
      return k.box("", k.t("headline", "H") + '<div class="cols">' +
        '<div class="col l"><div class="lb">' + (k.has("left_label") || c.edit ? k.t("left_label", "", "span") : "Not this") + "</div>" + k.t("left", "tx") + "</div>" +
        '<div class="col r"><div class="lb">' + (k.has("right_label") || c.edit ? k.t("right_label", "", "span") : "This") + "</div>" + k.t("right", "tx") + "</div></div>");
    } });

  // CLOSER / CTA
  add({ id: "cta-comment", name: "Comment a word", group: "Closer", roles: ["close"], photos: 0,
    fields: ["kicker", "headline", "cta", "body"],
    html: function (s, c, k) {
      return k.box("", k.t("kicker", "K") + k.t("headline", "H") + '<div class="say">Comment</div>' + k.t("cta", "bubble") + k.t("body", "B"));
    } });

  add({ id: "cta-save", name: "Save this", group: "Closer", roles: ["close"], photos: 0,
    fields: ["headline", "body", "cta"],
    html: function (s, c, k) {
      return '<div class="bm">' + SVG.bookmark + "</div>" + k.box("", k.t("headline", "H") + k.t("body", "B") + k.t("cta", "pill"));
    } });

  add({ id: "cta-photo", name: "Photo closer", group: "Closer", roles: ["close"], photos: 1, tone: "on-dark", light: true,
    fields: ["kicker", "headline", "cta", "body", "photo"],
    html: function (s, c, k) {
      return k.photo() + '<div class="scrim"></div>' + k.box("", k.t("kicker", "K") + k.t("headline", "H") + k.t("cta", "pill") + k.t("body", "B"));
    } });

  add({ id: "cta-follow", name: "Follow me", group: "Closer", roles: ["close"], photos: 1,
    fields: ["headline", "body", "cta", "photo"],
    html: function (s, c, k) {
      return '<div class="av">' + k.photo() + "</div>" +
        k.box("", '<div class="nm">' + esc(c.name || "Your Name") + '</div><div class="hd">' + esc(c.handle || "") + "</div>" +
          k.t("headline", "H") + k.t("body", "B") + k.t("cta", "pill"));
    } });

  var BY_ID = {};
  L.forEach(function (d) { BY_ID[d.id] = d; });

  var ROLES = ["cover", "point", "list", "quote", "stat", "compare", "close"];

  /* Looks: a starting layout for each kind of slide, chosen per carousel. */
  var LOOKS = {
    "editorial": { name: "Editorial", roles: { cover: "photo-full", point: "editorial", list: "list-numbered", quote: "quote-classic", stat: "stat-giant", compare: "myth-truth", close: "cta-comment" } },
    "photo-story": { name: "Photo story", roles: { cover: "cover-magazine", point: "photo-window", list: "list-photo", quote: "quote-photo", stat: "stat-split", compare: "before-after", close: "cta-photo" } },
    "bold": { name: "Bold type", roles: { cover: "cover-sticker", point: "big-type", list: "checklist", quote: "quote-post", stat: "stat-ring", compare: "side-by-side", close: "cta-save" } },
    "soft": { name: "Soft & faith", roles: { cover: "photo-arch", point: "note-card", list: "steps-timeline", quote: "quote-verse", stat: "stat-giant", compare: "myth-truth", close: "cta-follow" } }
  };

  function layoutFor(slide, plan) {
    if (slide.layout && BY_ID[slide.layout]) return slide.layout;
    var look = LOOKS[(plan && plan.look) || "editorial"] || LOOKS.editorial;
    return look.roles[slide.role] || look.roles.point;
  }

  /* Theme -> CSS variables. */
  function lum(hex) {
    var m = String(hex || "").replace("#", "");
    if (m.length === 3) m = m.split("").map(function (x) { return x + x; }).join("");
    if (m.length !== 6) return 0.5;
    var rgb = [0, 2, 4].map(function (i) {
      var v = parseInt(m.substr(i, 2), 16) / 255;
      return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2];
  }
  function contrast(a, b) { var x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); }
  function onColor(bg, opts) {
    var best = opts[0];
    opts.forEach(function (o) { if (contrast(bg, o) > contrast(bg, best)) best = o; });
    return best;
  }
  function fillTheme(t) {
    var col = Object.assign({}, t.colors || {});
    col.bg = col.bg || "#FFFFFF"; col.ink = col.ink || "#111111"; col.accent = col.accent || "#C2410C";
    col.accent2 = col.accent2 || "color-mix(in srgb," + col.accent + " 22%," + col.bg + ")";
    col.muted = col.muted || "#888888";
    col.paper = col.paper || "color-mix(in srgb," + col.bg + " 55%, #ffffff)";
    col.dark = col.dark || (lum(col.bg) < 0.2 ? col.bg : col.ink);
    col.on_dark = col.on_dark || onColor(col.dark, [col.bg, col.ink, "#FFFFFF"]);
    col.on_accent = col.on_accent || onColor(col.accent, ["#FFFFFF", col.bg, col.ink, "#111111"]);
    return Object.assign({}, t, { colors: col });
  }

  function themeStyle(t) {
    t = fillTheme(t || {});
    var col = t.colors || {}, f = t.fonts || {};
    function q(n, fb) { return "'" + (n || fb) + "'," + fb; }
    var script = t.kicker === "caps" ? false : true;
    var v = {
      "--bg": col.bg, "--ink": col.ink, "--accent": col.accent, "--accent2": col.accent2, "--muted": col.muted,
      "--paper": col.paper, "--dark": col.dark, "--on-dark": col.on_dark, "--on-accent": col.on_accent,
      "--f-head": q(f.head, "serif"), "--f-body": q(f.body, "sans-serif"), "--f-script": q(f.script, "cursive"),
      "--head-weight": t.head_weight || 700, "--head-case": t.head_case || "none", "--head-track": t.head_track || "-0.01em",
      "--radius": (t.radius == null ? 36 : t.radius) + "px", "--quote-style": t.quote_italic ? "italic" : "normal",
      "--kicker-font": script ? q(f.script, "cursive") : q(f.body, "sans-serif"),
      "--kicker-case": script ? "none" : "uppercase", "--kicker-track": script ? "0" : ".18em",
      "--kicker-weight": 700, "--kicker-size": script ? "62px" : "30px"
    };
    /* Optional per-layout accents a brand can set (tape on note cards, bookmark on save slides, avatar circle on post cards). */
    if (col.tape) v["--tape-bg"] = col.tape;
    if (col.bookmark) v["--bm-fill"] = col.bookmark;
    if (col.photo_hl) v["--photo-hl"] = col.photo_hl;
    if (col.avatar) { v["--av-bg"] = col.avatar; v["--av-fg"] = onColor(col.avatar, ["#FFFFFF", "#111111"]); }
    return Object.keys(v).map(function (key) { return key + ":" + v[key]; }).join(";");
  }

  /* Render one slide to an HTML string.
     ctx: {i, n, theme, edit, photoUrl, name, handle, show_handle, show_numbers, show_swipe} */
  function render(slide, ctx, plan) {
    var id = layoutFor(slide, plan);
    var d = BY_ID[id];
    var c = Object.assign({ photoUrl: function (x) { return x; } }, ctx);
    var k = kit(slide, c);
    var body = d.html(slide, c, k);
    var tone = d.tone || "";
    var light = d.light ? " light" : "";
    var chrome = "";
    if (c.show_handle !== false || c.show_numbers !== false) {
      chrome += '<div class="chr' + light + '"><span>' + (c.show_handle !== false ? esc(c.handle || "") : "") + "</span><span>" +
        (c.show_numbers !== false && c.n ? (c.i + 1) + " / " + c.n : "") + "</span></div>";
    }
    if (c.show_swipe !== false && c.n && c.i < c.n - 1 && id !== "cover-sticker") chrome += '<div class="swipe' + light + '">' + SVG.arrow + "</div>";
    if (id === "cover-magazine" || id === "editorial") chrome = chrome.replace(/<div class="chr[^"]*">.*?<\/div>/, "");
    return '<div class="sio L-' + id + " " + tone + (c.edit ? " editing" : "") + '" data-layout="' + id + '" style="' + themeStyle(c.theme) + '">' + body + chrome + "</div>";
  }

  /* Shrink words until they fit their box. Call after the slide is in the page and fonts are loaded. */
  function fit(el) {
    var boxes = el.querySelectorAll(".fitbox");
    Array.prototype.forEach.call(boxes, function (box) {
      var fi = box.firstElementChild;
      var k = 1;
      box.style.setProperty("--k", k);
      function over() {
        if (fi.scrollHeight > box.clientHeight + 2) return true;
        var kids = fi.querySelectorAll("*");
        for (var j = 0; j < kids.length; j++) {
          var e = kids[j];
          if (e.scrollWidth > e.clientWidth + 2 && getComputedStyle(e).display !== "inline") return true;
        }
        return false;
      }
      var guard = 0;
      while (over() && k > 0.4 && guard++ < 40) { k -= 0.04; box.style.setProperty("--k", k.toFixed(2)); }
    });
    Array.prototype.forEach.call(el.querySelectorAll("[data-fitw]"), function (e) {
      var size = parseFloat(getComputedStyle(e).fontSize), guard = 0;
      while (e.scrollWidth > e.parentElement.clientWidth && size > 40 && guard++ < 60) { size -= 4; e.style.fontSize = size + "px"; }
    });
  }

  root.CarouselStudio = {
    LAYOUTS: L, BY_ID: BY_ID, LOOKS: LOOKS, ROLES: ROLES, FIELD_HINTS: PH,
    render: render, fit: fit, layoutFor: layoutFor, themeStyle: themeStyle, plain: plain
  };
})(typeof window !== "undefined" ? window : this);
