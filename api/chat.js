const fs = require("fs");
const path = require("path");

const DEFAULT_MODEL = "openai/gpt-oss-120b";
const ROLES = ["General reasoner", "Skeptical reviewer", "Practical adviser"];
const HARNESS_PATH = path.join(process.cwd(), "backend", "harness.txt");

function getHarness(name, otherNames, role, round, maxRounds) {
	const values = {
		AI_NAME: name,
		NUM_AIS: "3",
		OTHER_AI_NAMES: otherNames,
		ROLE: role,
		ROUND: String(round),
		MAX_ROUNDS: String(maxRounds),
		MAX_WORDS_PER_TURN: "200",
	};

	return Object.entries(values).reduce(
		(text, [key, value]) => text.split(`{{${key}}}`).join(value),
		fs.readFileSync(HARNESS_PATH, "utf8")
	);
}

async function getAnswer(model, messages) {
	const response = await fetch("https://api.groq.com/openai/v1/chat/completions", {
		method: "POST",
		headers: {
			Authorization: `Bearer ${process.env.GROQ_API_KEY}`,
			"Content-Type": "application/json",
		},
		body: JSON.stringify({
			model,
			messages,
			max_completion_tokens: 2048,
		}),
	});

	const result = await response.json();
	if (!response.ok) {
		console.error("Groq request failed:", result?.error?.message || response.status);
		throw new Error("The AI service could not complete the request.");
	}

	const answer = result?.choices?.[0]?.message?.content;
	if (typeof answer !== "string" || !answer.trim()) {
		throw new Error("The AI service returned an empty answer.");
	}
	return answer.trim();
}

module.exports = async function handler(req, res) {
	if (req.method !== "POST") {
		res.setHeader("Allow", "POST");
		return res.status(405).json({ error: "Use POST to send a prompt." });
	}

	const prompt = req.body?.prompt;
	if (typeof prompt !== "string" || !prompt.trim() || prompt.length > 4000) {
		return res.status(400).json({ error: "Enter a prompt of up to 4,000 characters." });
	}
	if (!process.env.GROQ_API_KEY) {
		return res.status(500).json({ error: "Add GROQ_API_KEY to the Vercel environment variables." });
	}

	const rounds = Number(process.env.ROUNDS || "2");
	if (!Number.isInteger(rounds) || rounds < 1 || rounds > 4) {
		return res.status(500).json({ error: "ROUNDS must be a number from 1 to 4." });
	}

	const models = [
		process.env.MODEL_1 || DEFAULT_MODEL,
		process.env.MODEL_2 || DEFAULT_MODEL,
		process.env.MODEL_3 || DEFAULT_MODEL,
	];
	const participants = models.map((model, index) => ({
		name: `AI ${index + 1}`,
		model,
		role: ROLES[index],
	}));
	const history = [{ role: "user", content: prompt.trim() }];
	const transcript = [{ round: 0, name: "You", text: prompt.trim() }];

	try {
		for (let round = 1; round <= rounds; round += 1) {
			if (round > 1) {
				history.push({
					role: "user",
					content: `Continue the discussion. This is round ${round} of ${rounds}.`,
				});
			}

			for (const participant of participants) {
				const otherNames = participants
					.filter((other) => other.name !== participant.name)
					.map((other) => other.name)
					.join(", ");
				const systemPrompt = getHarness(
					participant.name,
					otherNames,
					participant.role,
					round,
					rounds
				);
				const text = await getAnswer(participant.model, [
					{ role: "system", content: systemPrompt },
					...history,
				]);

				transcript.push({ round, name: participant.name, text });
				history.push({ role: "assistant", content: `${participant.name}: ${text}` });
			}
		}

		return res.status(200).json({ transcript });
	} catch (error) {
		console.error("Discussion failed:", error);
		return res.status(502).json({
			error: error.message || "The AI service could not complete the request.",
		});
	}
};
