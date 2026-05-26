---
title: "Anthropic let AI agents trade with each other. The stronger model won every time."
description: "Project Deal: 69 employees, 186 deals, one uncomfortable finding — agent quality determines outcomes, and the losers don't notice."
pubDate: "May 26 2026"
heroImage: "/blog-placeholder-about.jpg"
---

Anthropic ran an experiment called Project Deal. Sixty-nine employees. One week. Each person got a $100 budget. Claude agents did all the buying and selling. The humans only stepped in at the end to physically hand over the goods — snowboards, original artwork, a bag of 19 ping-pong balls.

The agents struck 186 deals across more than 500 listed items. Over $4,000 changed hands. The marketplace worked. Agents wrote listings, found matches, proposed prices, fielded counteroffers, and closed — all in natural language over Slack. No human intervention.

That is the headline. The finding that matters is what happened when they changed the model.

## Four marketplaces, one secret

Anthropic ran four marketplace variants simultaneously. Two used Claude Opus 4.5 — the frontier model — for every agent. Two randomly assigned participants either Opus or Claude Haiku 4.5, the smaller, faster, cheaper model. Participants did not know which model was representing them in which run.

The only variable was model capability. Same instructions. Same preferences. Same items. Different brains.

The results were not subtle.

Opus sellers extracted $3.64 more on average for the same item compared to Haiku sellers. Opus buyers paid $2.45 less on average. Opus users closed about two more deals each. When an Opus seller negotiated against a Haiku buyer, the average transaction price was $24.18 — about 30 percent higher than Opus-to-Opus deals.

One item crystallizes the gap. A broken folding bike. Same seller. Same buyer. Opus sold it for $65. Haiku sold it for $38. That is a 70 percent price difference. Same bike. Same market. Different model.

## Nobody noticed they were losing

Here is the part that should make people uncomfortable.

After each run, participants rated how fair their deals felt on a scale of one to seven. Haiku users scored 4.06. Opus users scored 4.05. Identical. The gap was not just statistically insignificant — it was nonexistent.

Twenty-eight participants used both model types across different runs. Seventeen said Opus was better. Eleven actually preferred Haiku.

People on the losing end of agent quality gaps did not feel like they were losing. They walked away satisfied, holding less money and worse deals, convinced the outcome was fair.

Anthropic's own write-up calls this "an uncomfortable implication." That is the right phrase.

## Prompting does not matter

Participants gave their agents all kinds of instructions. Some said "be friendly and community-minded." Some said "lowball aggressively." One told their agent to negotiate in the style of an exasperated cowboy down on his luck.

The cowboy bit was entertaining. The instructions had no measurable effect on outcomes. Aggressive sellers got higher prices only because they set higher opening prices. The negotiation style itself did not move the needle.

What moved the needle was the model. Not the prompt. Not the strategy. The raw capability of the model doing the negotiating.

This matters because the industry has spent two years obsessing over prompt engineering. Project Deal suggests that for real economic outcomes, model selection matters more than any amount of prompt tuning. Pick a weaker model and no amount of clever instruction will close the gap.

## This is not theoretical

Forty-six percent of participants said they would pay for an agent service like this. That is nearly half of a technically sophisticated group, after one week, wanting to hand over real money for autonomous agent negotiation.

The demand signal is clear. People want agents to transact on their behalf. The question is not whether agent-mediated commerce will happen. It is already happening. The question is what happens when some people show up to the marketplace with Opus and others show up with Haiku — and nobody knows who has what.

The policy and legal frameworks for this do not exist. Anthropic acknowledges this directly. When an agent buys something on your behalf, who is responsible for a bad deal? If a stronger model systematically extracts value from a weaker one, is that fraud? Competition? Just a better negotiating partner?

None of these questions have answers. The experiment ran inside a single company with gift cards and Slack channels. Scale that to millions of agents transacting across the internet and the dynamics get ugly fast.

## The quiet arms race

Project Deal is not just about market fairness. It surfaces an incentive structure that almost guarantees an arms race.

If a better model gets you better prices, and the gap is invisible to the person on the other side, then every participant in an agent-mediated market has a strong incentive to use the most capable model available. Not because they want to exploit anyone. Because they do not want to be the one getting exploited without knowing it.

That pushes everyone toward the frontier models. It concentrates power in the hands of the labs that build them. It makes model quality an economic variable that compounds across every transaction.

Anthropic is not hiding this. The experiment was designed to surface exactly these dynamics. But surfacing them and solving them are different things.

The broken bike sold for $65 under Opus and $38 under Haiku. If you were the seller, you want Opus. If you were the buyer, you want Opus too — it paid $2.45 less on average. The stronger model wins on both sides of the trade.

That is not a bug in the experiment. It is a property of the technology. And it scales.
