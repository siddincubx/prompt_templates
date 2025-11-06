class Template{
    text string
    variables string[]
    title string
    category string @description(#"
        Category associated with the template, used for categorization and search.
    "#)
}

function CreateTemplate(requirement : string) -> Template{
    client CustomGemini
    prompt #"
        Create a prompt for fulfilling the requirement:
        {{ requirement }}

        The prompt generated must be in template format that includes placeholders for variables that can be filled in later.
        The prompt generated is expected to be in EJS format.

        IMPORTANT: DO NOT provide the template for requirement itself but generate a prompt that will fulfill this requirement.
        
        Provide the template text and a list of variable names used in the template. 
        Think about the requirement carefully and find the ambiguous entities. 
        These entities should be converted into variables in the template.
        BE CAREFUL TO NOT CREATE DUPLICATE VARIABLES. DO NOT CREATE VARIABLES THAT ARE REDUNDANT.

        IMPORTANT: DO NOT provide the template for requirement itself but generate a prompt to fulfill this requirement.

        for example:
        Requirement: I want to generate personalized email invitations for a conference.
        Output: 
        Generate a personalized email invitation for the <%= conferenceName %> conference, taking place from <%= startDate %> to <%= endDate %> at <%= location %>. 
        The email should be addressed to <%= recipientName %>.  Use a friendly and professional tone.
        Begin with a captivating subject line: '<%= subjectLine %>'
        In the email body, briefly introduce the conference, highlighting its key themes: <%= conferenceThemes %>. Mention that <%= speakerName %> will be a keynote speaker.
        Personalize the invitation by mentioning <%= personalizedMessage %>. 
        Include a call to action, encouraging the recipient to register for the conference via the following link: <%= registrationLink %>.  Offer an early bird discount if they register before <%= earlyBirdDeadline %>, specifying the discount as <%= earlyBirdDiscount %>.
        Include a brief agenda summary: <%= agendaSummary %>. 
        Conclude the email with a professional closing and signature from <%= senderName %> (<%= senderTitle %>).
        Ensure the email is visually appealing and easy to read.
        {{ ctx.output_format }}
    "#
    
}

test template_conference_email_invitation {
    functions [CreateTemplate]
    args {
        requirement #"
            I want to generate personalized email invitations for a conference. 
        "#
    }
}

test template_apologise_mistake_chat_msg {
    functions [CreateTemplate]
    args {
        requirement #"
            I want to generate a personalized apology message for a mistake made in a chat conversation.
        "#
    }
}
test template_product_description {
    functions [CreateTemplate]
    args {
        requirement #"
            I want to generate an engaging product descriptions for an e-commerce website. 
        "#
    }
}