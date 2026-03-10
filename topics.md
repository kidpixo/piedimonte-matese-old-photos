---
layout: page
title: Topics
permalink: /topics/
exclude_from_nav: true
---

<ul style="list-style:none; padding:0;">
{% assign topics_sorted = site.topics | sort: "title" %}
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
