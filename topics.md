---
lang: it
translation_key: topics
layout: page
title: Topics
exclude_from_nav: true
---

<ul style="list-style:none; padding:0;">
{% comment %}ADR-010: no per-file permalink; `permalink: pretty` maps topics.md ->
/topics/ and en/topics.md -> /en/topics/. Only this language's topics are listed.{% endcomment %}
{% assign page_lang = page.lang | default: site.default_lang %}
{% assign topics_visible = "" | split: "" %}
{% for topic in site.topics %}
  {% unless topic.lang and topic.lang != page_lang %}
    {% assign topics_visible = topics_visible | push: topic %}
  {% endunless %}
{% endfor %}
{% assign topics_sorted = topics_visible | sort: "title" %}
{% for topic in topics_sorted %}
  <li style="margin-bottom: 1.25rem; border-bottom: 1px solid #eee; padding-bottom: 1rem;">
    <a href="{{ topic.url | relative_url }}"><strong>{{ topic.title }}</strong></a>
    {% if topic.excerpt %}
      <p style="margin:0.25rem 0 0; font-size:0.9em; opacity:0.8;">{{ topic.excerpt | strip_html | truncate: 160 }}</p>
    {% endif %}
    {% if topic.featured_photos %}
      <small style="opacity:0.6;">{{ topic.featured_photos.size }} photo{{ topic.featured_photos.size | minus: 1 | at_least: 1 | floor | at_most: 1 | minus: 1 | abs | pluralize: "", "s" }}</small>
    {% endif %}
  </li>
{% endfor %}
</ul>
