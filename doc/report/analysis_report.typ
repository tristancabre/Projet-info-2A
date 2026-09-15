// Simple numbering for non-book documents
#let equation-numbering = "(1)"
#let callout-numbering = "1"
#let subfloat-numbering(n-super, subfloat-idx) = {
  numbering("1a", n-super, subfloat-idx)
}

// Theorem configuration for theorion
// Simple numbering for non-book documents (no heading inheritance)
#let theorem-inherited-levels = 0

// Theorem numbering format (can be overridden by extensions for appendix support)
// This function returns the numbering pattern to use
#let theorem-numbering(loc) = "1.1"

// Default theorem render function
#let theorem-render(prefix: none, title: "", full-title: auto, body) = {
  if full-title != "" and full-title != auto and full-title != none {
    strong[#full-title.]
    h(0.5em)
  }
  body
}
// Some definitions presupposed by pandoc's typst output.
#let content-to-string(content) = {
  if content.has("text") {
    content.text
  } else if content.has("children") {
    content.children.map(content-to-string).join("")
  } else if content.has("body") {
    content-to-string(content.body)
  } else if content == [ ] {
    " "
  }
}

#let horizontalrule = line(start: (25%,0%), end: (75%,0%))

#let endnote(num, contents) = [
  #stack(dir: ltr, spacing: 3pt, super[#num], contents)
]

#show terms.item: it => block(breakable: false)[
  #text(weight: "bold")[#it.term]
  #block(inset: (left: 1.5em, top: -0.4em))[#it.description]
]

// Some quarto-specific definitions.

#show raw.where(block: true): set block(
    fill: luma(230),
    width: 100%,
    inset: 8pt,
    radius: 2pt
  )

#let block_with_new_content(old_block, new_content) = {
  let fields = old_block.fields()
  let _ = fields.remove("body")
  if fields.at("below", default: none) != none {
    // TODO: this is a hack because below is a "synthesized element"
    // according to the experts in the typst discord...
    fields.below = fields.below.abs
  }
  block.with(..fields)(new_content)
}

#let empty(v) = {
  if type(v) == str {
    // two dollar signs here because we're technically inside
    // a Pandoc template :grimace:
    v.matches(regex("^\\s*$")).at(0, default: none) != none
  } else if type(v) == content {
    if v.at("text", default: none) != none {
      return empty(v.text)
    }
    for child in v.at("children", default: ()) {
      if not empty(child) {
        return false
      }
    }
    return true
  }

}

// Subfloats
// This is a technique that we adapted from https://github.com/tingerrr/subpar/
#let quartosubfloatcounter = counter("quartosubfloatcounter")

#let quarto_super(
  kind: str,
  caption: none,
  label: none,
  supplement: str,
  position: none,
  subcapnumbering: "(a)",
  body,
) = {
  context {
    let figcounter = counter(figure.where(kind: kind))
    let n-super = figcounter.get().first() + 1
    set figure.caption(position: position)
    [#figure(
      kind: kind,
      supplement: supplement,
      caption: caption,
      {
        show figure.where(kind: kind): set figure(numbering: _ => {
          let subfloat-idx = quartosubfloatcounter.get().first() + 1
          subfloat-numbering(n-super, subfloat-idx)
        })
        show figure.where(kind: kind): set figure.caption(position: position)

        show figure: it => {
          let num = numbering(subcapnumbering, n-super, quartosubfloatcounter.get().first() + 1)
          show figure.caption: it => block({
            num.slice(2) // I don't understand why the numbering contains output that it really shouldn't, but this fixes it shrug?
            [ ]
            it.body
          })

          quartosubfloatcounter.step()
          it
          counter(figure.where(kind: it.kind)).update(n => n - 1)
        }

        quartosubfloatcounter.update(0)
        body
      }
    )#label]
  }
}

// callout rendering
// this is a figure show rule because callouts are crossreferenceable
#show figure: it => {
  if type(it.kind) != str {
    return it
  }
  let kind_match = it.kind.matches(regex("^quarto-callout-(.*)")).at(0, default: none)
  if kind_match == none {
    return it
  }
  let kind = kind_match.captures.at(0, default: "other")
  kind = upper(kind.first()) + kind.slice(1)
  // now we pull apart the callout and reassemble it with the crossref name and counter

  // when we cleanup pandoc's emitted code to avoid spaces this will have to change
  let old_callout = it.body.children.at(1).body.children.at(1)
  let old_title_block = old_callout.body.children.at(0)
  let children = old_title_block.body.body.children
  let old_title = if children.len() == 1 {
    children.at(0)  // no icon: title at index 0
  } else {
    children.at(1)  // with icon: title at index 1
  }

  // TODO use custom separator if available
  // Use the figure's counter display which handles chapter-based numbering
  // (when numbering is a function that includes the heading counter)
  let callout_num = it.counter.display(it.numbering)
  let new_title = if empty(old_title) {
    [#kind #callout_num]
  } else {
    [#kind #callout_num: #old_title]
  }

  let new_title_block = block_with_new_content(
    old_title_block,
    block_with_new_content(
      old_title_block.body,
      if children.len() == 1 {
        new_title  // no icon: just the title
      } else {
        children.at(0) + new_title  // with icon: preserve icon block + new title
      }))

  align(left, block_with_new_content(old_callout,
    block(below: 0pt, new_title_block) +
    old_callout.body.children.at(1)))
}

// 2023-10-09: #fa-icon("fa-info") is not working, so we'll eval "#fa-info()" instead
#let callout(body: [], title: "Callout", background_color: rgb("#dddddd"), icon: none, icon_color: black, body_background_color: white) = {
  block(
    breakable: false, 
    fill: background_color, 
    stroke: (paint: icon_color, thickness: 0.5pt, cap: "round"), 
    width: 100%, 
    radius: 2pt,
    block(
      inset: 1pt,
      width: 100%, 
      below: 0pt, 
      block(
        fill: background_color,
        width: 100%,
        inset: 8pt)[#if icon != none [#text(icon_color, weight: 900)[#icon] ]#title]) +
      if(body != []){
        block(
          inset: 1pt, 
          width: 100%, 
          block(fill: body_background_color, width: 100%, inset: 8pt, body))
      }
    )
}




#let article(
  title: none,
  subtitle: none,
  authors: none,
  keywords: (),
  date: none,
  abstract-title: none,
  abstract: none,
  thanks: none,
  cols: 1,
  lang: "en",
  region: "US",
  font: none,
  fontsize: 11pt,
  title-size: 1.5em,
  subtitle-size: 1.25em,
  heading-family: none,
  heading-weight: "bold",
  heading-style: "normal",
  heading-color: black,
  heading-line-height: 0.65em,
  mathfont: none,
  codefont: none,
  linestretch: 1,
  sectionnumbering: none,
  linkcolor: none,
  citecolor: none,
  filecolor: none,
  toc: false,
  toc_title: none,
  toc_depth: none,
  toc_indent: 1.5em,
  doc,
) = {
  // Set document metadata for PDF accessibility
  set document(title: title, keywords: keywords)
  set document(
    author: authors.map(author => content-to-string(author.name)).join(", ", last: " & "),
  ) if authors != none and authors != ()
  set par(
    justify: true,
    leading: linestretch * 0.65em
  )
  set text(lang: lang,
           region: region,
           size: fontsize)
  set text(font: font) if font != none
  show math.equation: set text(font: mathfont) if mathfont != none
  show raw: set text(font: codefont) if codefont != none

  set heading(numbering: sectionnumbering)

  show link: set text(fill: rgb(content-to-string(linkcolor))) if linkcolor != none
  show ref: set text(fill: rgb(content-to-string(citecolor))) if citecolor != none
  show link: this => {
    if filecolor != none and type(this.dest) == label {
      text(this, fill: rgb(content-to-string(filecolor)))
    } else {
      text(this)
    }
   }

  let has-title-block = title != none or (authors != none and authors != ()) or date != none or abstract != none
  if has-title-block {
    place(
      top,
      float: true,
      scope: "parent",
      clearance: 4mm,
      block(below: 1em, width: 100%)[

        #if title != none {
          align(center, block(inset: 2em)[
            #set par(leading: heading-line-height) if heading-line-height != none
            #set text(font: heading-family) if heading-family != none
            #set text(weight: heading-weight)
            #set text(style: heading-style) if heading-style != "normal"
            #set text(fill: heading-color) if heading-color != black

            #text(size: title-size)[#title #if thanks != none {
              footnote(thanks, numbering: "*")
              counter(footnote).update(n => n - 1)
            }]
            #(if subtitle != none {
              parbreak()
              text(size: subtitle-size)[#subtitle]
            })
          ])
        }

        #if authors != none and authors != () {
          let count = authors.len()
          let ncols = calc.min(count, 3)
          grid(
            columns: (1fr,) * ncols,
            row-gutter: 1.5em,
            ..authors.map(author =>
                align(center)[
                  #author.name \
                  #author.affiliation \
                  #author.email
                ]
            )
          )
        }

        #if date != none {
          align(center)[#block(inset: 1em)[
            #date
          ]]
        }

        #if abstract != none {
          block(inset: 2em)[
          #text(weight: "semibold")[#abstract-title] #h(1em) #abstract
          ]
        }
      ]
    )
  }

  if toc {
    let title = if toc_title == none {
      auto
    } else {
      toc_title
    }
    block(above: 0em, below: 2em)[
    #outline(
      title: toc_title,
      depth: toc_depth,
      indent: toc_indent
    );
    ]
  }

  doc
}

#set table(
  inset: 6pt,
  stroke: none
)
#let brand-color = (:)
#let brand-color-background = (:)
#let brand-logo = (:)

#set page(
  paper: "a4",
  margin: (x: 1.5cm,y: 2.0cm,),
  numbering: "1",
  columns: 1,
)

#show: doc => article(
  font: ("Libertinus Serif",),
  fontsize: 11pt,
  sectionnumbering: "1.1.a",
  toc_title: [Table of contents],
  toc_depth: 3,
  doc,
)

#import "model.typ": project_template

#show: body => project_template(
  title: [Analysis Report on the NEO-Watch Project],
  team: [Team 7],
  authors: ([Tristan Cabre], [Gabrielle Causse], [Albane Krob], [Noé Chauvin]),
  tutor: [M. Ricciardi],
  project: [2nd-Year Computer Science Project – 2026–2027 Academic Year],
  body
)
#heading(level: 1, numbering: none)[Introduction]
<introduction>
Who has never watched shooting stars in the sky as a kid, wondering what they were and where they came from ? By growing up, we all learned that theses beatiful lights were due to the high-speed dust of meteorite coming in the atmosphere, before it inevitably destroy it. However, what would happen if it was not just the dust of the meteorit, but the meteorit itself which was coming straight to us through the atmosphere ? Wouldn't we like to know ? And if we do, could we avoid it ? At least, we know that the dinosaurs didn't ask themselves this question…

As humanity was a little more concerned about these small Solar System bodies than its predecessors on Earth, the US government tasked NASA with cataloguing 90% of Near-Earth Objects (NEOs) with a diameter greater than 1 km within ten years. Additionally, in 2016, NASA was asked not only to list the threats, but also to create a solution in case of an unavoidable collision trajectory. With this in mind, NASA launched the space mission DART (Double Asteroid Redirection Test) in 2022, resulting in a success by significantly changing the trajectory of the small asteroid Dimorphos.

The objective of this project is to develop an intuitive and secured application, coded in Python, that queries NASA's API in order to track and monitor these Near-Earth Objects. Designed to handle distinct access levels for regular users and administrators, the system provides an interactive dashboard highlighting close approaches and hazardous celestial bodies.

From querying specific NEOs by size or trajectory to managing personalized favorites and registering newly spotted objects, the application delivers actionable planetary defense insights at anyone's fingertips. The first part of this report will be devoted to the preliminary analysis of the project, detailing the functional requirements, constraints, and team organization. The second part will address the technical design, including the use case and activity diagrams, as well as the database schema and architecture.

#pagebreak()
= Conception of the application
<conception-of-the-application>
== Specifications
<specifications>
NEO-Watch addresses a genuine planetary-defense concern by tracking Near-Earth Objects (asteroids and comets). Beyond this evocative framing, the project raises several concrete stakes. First, the application depends entirely on NASA's public API for its data, which makes data reliability and availability critical success factors: any downtime or inconsistency on NASA's side directly affects the quality of the service offered to users. Second, the system must guarantee data integrity across successive updates, since NEOs created manually by users (feature F4) must never be overwritten when the database is refreshed with new data from NASA --- a non-trivial synchronization and versioning challenge. Third, NEO-Watch must serve two distinct audiences with different needs: casual users who simply want a quick overview through the dashboard and alerts, and more engaged users who will use advanced features such as favorites tracking, comparisons, or statistics; the interface and architecture must accommodate both without becoming complex. Finally, security and access control are important, since the application distinguishes between regular users and administrators and must protect personal data such as favorites, search history, and alert configurations, while also ensuring that time-sensitive alerts are computed and delivered promptly to remain useful.

The core of NEO-Watch revolves around six mandatory features. User and access management (F1) establishes two categories of accounts : regular users, who authenticate via login and password to access their personal space, and administrators, who can manage accounts, consult connection history, and trigger updates of NEO data from NASA's API. A personalized dashboard (F2) then gives each user a synthetic view of relevant information, such as upcoming close approaches, the number of potentially hazardous NEOs, the closest object over a given period, and highlights drawn from the user's own favorites. The browsing feature (F3) allows users to search and filter NEOs by criteria such as name, identifier, size, or next passage date, with sortable results and export capabilities. Users can also contribute directly to the dataset through NEO creation (F4), provided that these manually added entries are preserved during subsequent synchronizations with NASA's API. A favorites management feature (F5) lets users build a personal watchlist, keeping a history of each favorite NEO's distance from Earth over time and allowing that history to be exported as graphs. Finally, the alerting feature (F6) enables users to define custom notification rules (for instance, being warned when an asteroid above a certain size passes within a specified distance of Earth) with notifications delivered at the user's next login.

Beyond these mandatory features, several optional enhancements can enrich the application. Users could compare multiple NEOs side by side on criteria such as size or danger level (FO1), consult their own search history over the past thirty days while administrators access any user's history (FO2), or explore built-in statistics such as monthly approach counts or size distributions (FO3). The application could also recommend particularly interesting NEOs to observe based on combined criteria of size, rarity, or danger (FO4). The application could also support email communication between users and administrators for bug reports or account notifications (FO5), allow users to propose corrections to NEO data for administrator review (FO6), automate the periodic reloading of NASA's data through batch processing (FO7), and, on a lighter note, let users export NASA's daily astronomy picture (FO8).

The mandatory technology stack centers on Python, with FastAPI handling the backend, PostgreSQL providing persistent storage, pytest supporting the test suite, and Git managing version control. On the frontend side, we must choose between a Python-native interface, using a framework such as Streamlit, Tkinter, or Reflex, and a JavaScript-based solution built with React or Vue. A major constraint stems from the read-only nature of NASA's API: since the application can only retrieve data and never write back to NASA's database, any user-proposed modification (FO6) must remain purely internal, and the refresh strategy for NEO data is bound by whatever availability and rate limits NASA imposes. This, in turn, requires careful data-synchronization logic capable of distinguishing NASA-sourced records from user-created ones, so that periodic updates never silently overwrite manually added NEOs. Role-based access control between regular users and administrators must be enforced consistently at the API level rather than only in the interface, to guarantee that sensitive operations, such as triggering a data update or viewing another user's history, remain properly restricted. Storing time-series data, such as the distance history of favorite NEOs or thirty-day search logs, also calls for a schema specifically designed to handle historical records efficiently in PostgreSQL. Lastly, the delivery of alerts and email notifications introduces a scheduling constraint, since these features require either a background job triggered at login or a periodic scheduled task, each with different trade-offs in terms of complexity and responsiveness.

== Conception's choices
<conceptions-choices>
The functioning of the application had to be discussed within the group in order to make the best decisions and to justify our choices throughout the project. This document aims to summarize the main points debated so far, along with the reasoning behind each decision.

The first point of debate in the design of our application was the distinction between the two types of users. From the very beginning, we understood that having both Administrators and Visitors would be necessary, given the range of features to be implemented.

This distinction is needed because some services and mandatory features require internal access to information that ordinary users should not have access to, such as the connection history of other users. Allowing every user unrestricted access to this kind of information would compromise the privacy of other users as well as the security of the application.

This is why an authentication controller is required. It must identify the user upon login and grant access to the appropriate auser interface and set of tools depending on their role. In practice, Administrators can be seen as regular visitors with extended rights, allowing them to manage the application (for example, checking user activity), but not creating a completely separate category of user.

We decided to build the user interface with Streamlit. Instead of having Streamlit communicate directly with the database, we have to use FastAPI a backend API layer between the frontend and the data. Then, the path of a request will be as such : the Streamlit frontend calls the API, which forwards the request to a Controller, the Controller delegates the business logic to a Service layer which relies on a DAO (Data Access Object) to communicate with the database. This separation of concerns makes the application easier to maintain, and test, since each layer has a well-defined responsibility.

Through this interface, users will be able to browse the database and search for NEOs (Near-Earth Objects) using filters such as name, date, and composition of the asteroid. They will also be able to build a list of favourites among their searches and receive alerts when a NEO is approaching Earth. In addition, the application will allow users to generate summary statistics and export graphs in response to specific requests, giving them a way to visualize and analyze the data that matters to them.

To distinguish between visitors and administrators, we plan to use a boolean codification (add in an is\_admin field) associated with each user account. This flag will be checked at the Controller level to determine whether a given request should be authorized, ensuring that sensitive endpoints (such as those exposing other users' connection history) remain restricted to Administrators only.

Finally, this range of features will require reliable access to the database. We will use PostgreSQL for storage. Rather than allowing each layer or each user session to open its own direct connection, access to the database will be centralized through the DAO layer, using a connection pool. This will help avoid conflicting access, while still allowing multiple users to use the application simultaneously.

== Feature description
<feature-description>
== Group organisation
<group-organisation>
The Gantt chart below represents the work that we plan to accomplish throughout the duration of the project. We decided to divide the project into three main phases: analysis, development and programming, and report writing and oral presentation preparation. This schedule is not intended to be followed to the letter, but rather to provide the group with a general framework for organizing and distributing the workload. It should help us avoid overloading, particularly towards the end of the project or during periods when we have exams. For this reason, we have decided to maintain a steady pace throughout the project.

Dividing the tasks required to successfully complete the project among the four members of the group is essential to keep track of our progress and deadlines. It is also a way to ensure a balanced distribution of the workload in the group. This organization should also make it easier to identify the tasks that have been completed and those that still need to be addressed and upgraded.

Furthermore, the immersion days will provide us with additional opportunities to make significant progress on the project. During these days, we will be able to complete an important part of the planned work, work together more efficiently, or focus on specific issues that may require further discussion and attention. These periods of more intensive group work should help us to be up to date with our own schedule.

The report will be written progressively throughout the project. Nevertheless, most of the writing will take place during the last few weeks. Indeed, we will need to have a complete overview of the application before we can provide a detailed description of our work and explanations of the technical decisions we made. This will also allow us to include relevant explanations concerning any difficulties or technical issues encountered during the development process, as well as the solutions we implemented to correct them.

Finally, we aim to complete the main part of the project approximately one week before the final submission deadline. This period should give us enough time to review and test the application, finalize the report, prepare the oral presentation, and make any necessary corrections. It should also reduce the risk of having to complete a large amount of work at the last minute and being caught off guard.

We believe that this organization will contribute to the success of our project by helping us stay motivated, work efficiently, and remain a cohesive team.

== Work organisation
<work-organisation>
= Architecture of the Application
<architecture-of-the-application>
== Case use diagram
<case-use-diagram>
#figure([
#box(image("img/case_use_diagram.png"))
], caption: figure.caption(
position: bottom, 
[
Case use diagram
]), 
kind: "quarto-float-fig", 
supplement: "Figure", 
)


== Activity diagram
<activity-diagram>
#figure([
#box(image("img/Activity_diagramm.png"))
], caption: figure.caption(
position: bottom, 
[
Activity diagramm
]), 
kind: "quarto-float-fig", 
supplement: "Figure", 
)


== Physical data model
<physical-data-model>
#figure([
#box(image("img/data_model.png"))
], caption: figure.caption(
position: bottom, 
[
Physical data model
]), 
kind: "quarto-float-fig", 
supplement: "Figure", 
)


The physical data model represents the different databases used to operate the application. Each table stores a specific object. The tables are linked to one another through a primary key/foreign key system. The cardinalities are directly indicated on the diagram.

The two main objects in this application are users and asteroids, the latter also forming the core of the physical data model. The "NEO" table depends directly on NASA's API, whereas the "User" table stores information (pseudo, password, email,…) about the different users registered on the application.

The favourites and alerts are stored in separate tables so that they are not lost each time the data is refreshed through the API. These two tables also establish the link between users and the asteroids. The other tables store the information required to implement the functionalities specified in the requirements.

For example, the requirements state: "For each favourite NEO, a history of its distance from Earth must be maintained." We therefore need a "NeoDistanceHistory" table linked to the "Neo" table, which stores pairs of values consisting of a date and a distance. We choose the type of "distance" to be float because it is easier to build statistics then.

Another functionality that requires additional data tables is the history feature. We need to store all queries in a database, along with the corresponding user and the date on which the query was made. To achieve this, we defined two data tables: one for the search history ("SearchHistory") and the other for the users' connection history ("ConnectionLog").

== Class Diagram
<class-diagram>
#underline[Conceptual conception of the application Neo-Watch] \

Neo-Watch is an application dedicated to the monitoring of Near Earth Objects (NEOs). Its purpose is to let people search and follow NEOs, keep track on how their distance to Earth changes over time, and be alerted immediately when an object comes close to Earth. To manage access rights and demanded features in the application, we will separate administrators who are given extra rights to manage the platform itself (accounts, connection history, and the underlying NEO database) from common users, called visitors in this architecture.

The conceptual model is built directly from the class diagram of the application. It is organised in two complementary readings: first, the layered architecture that structures how the code is organised; second, the domain (business) classes that carry the actual concepts of the application, Users, NEOs, Alerts, Favourites, and their history.

#underline[Classes for the Business part] \

The domain classes are essential for this application.

=== Users
<users>
Every person who uses the application is represented by the class User, which represents what is common to all accounts: a pseudo, a password which is always stored hashed, thanks to the methods hash and check for the password. An email address is also stored and used to receive alerts. Two particular cases extend this class:

Visitor: This user is an ordinary visitor of the application. They can create an account, log in, save a password, build a list of favourite NEOs, receive notifications and search the database.

Administrator: This particular user inherits everything a Visitor can do, and additionally gets privileged actions. The administrators consulting the loggin history of the Neo, watch application, and searching, updating or deleting any account of a visitor.

This inheritance relationship (User \<- Visitor and Administrator). It could be said that an Administrator is a User with extended rights.

=== Near Earth Objects (NEO)
<near-earth-objects-neo>
The class Neo represents a Near Earth Object, with its descriptive characteristics: name, weight, size, composition, rarity, origin, its closest recorded day, and a distance to Earth. This distance is not a fixed, it evolves over time as the object continues its trajectory in the NASA database, which is precisely why it is built so that there can be a mechanism to keep track of it.

The NeoDistanceHistory class enables to folow how a NEO's distance to Earth evolves after each update of the database. Each Neo should own exactly one NeoDistanceHistory object. It is a component of the Neo itself, responsible for recording the evolution of the distance to Earth. Internally, it keeps a list of records (a date to reference the distance to Earth) which will give the opporutnity for a User to reconstruct its evolution, approach or leave over time.

This design keeps a clean separation of concerns: the Neo class describes what the object is, while NeoDistanceHistory describes how its distance behaves through time which will be the information Favourites and Alert rely on.

=== Favourites
<favourites>
A User can build a personal list of favourite NEOs through the Favourites class. Each Favourites entry links one User to one Neo.

=== Alerts and Notifications
<alerts-and-notifications>
Every User can define one or more Alert entries, each one relying on a condition to trigger the notification.

#figure([
#box(image("img/UML_diagram.png.png"))
], caption: figure.caption(
position: bottom, 
[
UML diagram
]), 
kind: "quarto-float-fig", 
supplement: "Figure", 
)


== Package Diagram
<package-diagram>
The following package diagram is meant to explain and describe, as precisely as possible, how the layers communicate and enable our application to function. Every request sent by a User, whether a Visitor or an Administrator, is handled through the API and its endpoints, which contact the Controller. The user has access to several actions, which are translated into methods in the Controller layer. Once a request is received, the Controller passes it to the Service layer, which relies on a separate Business package containing the classes built to handle the request's business logic. When the action has been processed, the DAO is used to query the database and retrieve the results. This data then flows back up through the chain it went through, Service layer and the Controller, which returns it to the User via the API. The DAO is the only layer in direct contact with the database (edited by NASA) so the results have to comme back in the said precedent order. Finally, you may observe that a Test addition is to be found in the upper right side of our diagram. Indeed, it represents the process of testing and checking whether our application functions correctly.

#figure([
#box(image("img/Diagramme_de_package.png"))
], caption: figure.caption(
position: bottom, 
[
Package Diagram of the application
]), 
kind: "quarto-float-fig", 
supplement: "Figure", 
)


#pagebreak()
#heading(level: 1, numbering: none)[Conclusion]
<conclusion>
#pagebreak()
#heading(level: 1, numbering: none)[Appendices]
<appendices>



