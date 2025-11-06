class PromptTrialResult{
    text string
}

function DoPromptTrial(promptText : string) -> PromptTrialResult{
    client CustomGemini
    prompt #"
        {{promptText}}
        {{ctx.output_format}}
    "#
}

test prompt_trial_linkedin_connection_request {
    functions [DoPromptTrial]
    args {
        promptText #"
            Craft a personalized LinkedIn connection request message to Santosh tiwari, who works as a Senior Software Engineer at Github. 

Start with a brief, engaging opening line that references something specific you found interesting on their profile, such as their experience in AI Agent workflows or their involvement in Software Engineering.

State your reason for connecting, mentioning a shared interest or connection.  For example, mention that you are also interested in AI and modern technology or that you noticed they are connected to none. If relevant, briefly mention how your expertise in Software Engineering with high focus on building reliable production based AI applications could be beneficial to them, or vice versa. 

Keep the message concise and focused on creating a mutually beneficial connection. End with a clear call to action, such as inviting them to connect and express your interest in learning more about their work at Github.

Aim for a friendly and professional tone, conveying genuine interest in connecting with them. The character count should not exceed Linkedin's limit.

Optionally, include a brief mention of got second prize in company hosted AI hackathon to further demonstrate your expertise.
        "#
    }
}