---
title: "What broke the deploy"
description: "A short post about the usual suspects when a site refuses to leave your laptop."
pubDate: "May 11 2026"
heroImage: "/blog-placeholder-5.jpg"
---

The worst part of a failed deploy is that it usually looks like a small problem wearing a fake moustache.

The stack says one thing. The logs say another. The platform says everything is healthy except the part that clearly is not. So you start the ritual.

First, check the build.
If the build fails, good. That means the problem is honest. You can see it.

Then check the output path.
Astro is happy to build a static site, but the deployment target still needs to know where the files went. If the app expects a server and you hand it a folder of HTML, it will stare at you like you have made a lifestyle choice.

After that, check the runtime assumptions.
Node version. Base image. Start command. Port binding. Static versus server output. These are the little things that cost an hour because they feel too small to be the real issue.

That is usually where the bug lives.
Not in the grand architecture. In the one assumption nobody wrote down.

This is why I prefer deployments that can be explained out loud without using the phrase "it depends." If the answer takes a whiteboard and a caffeine budget, the setup is already asking for trouble.

For this site, the fix was simple once the shape of the problem was clear:

- build the Astro site deterministically
- serve the generated `dist/` output
- stop pretending the platform can guess intent from vibes

That is the whole trick.
Not elegant. Not magical. Just enough structure that the next failure has fewer places to hide.

And that is what you want from infrastructure, really. Less poetry. Fewer surprises.
