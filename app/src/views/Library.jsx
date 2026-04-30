// Library view — literary corpus and topic model.
// Wired to /literature/topics when the corpus and model are loaded.

const SEED_AUTHORS = [
  { name: "Mary Antin", origin: "Russian Empire (Belarus)", era: "historic", work: "The Promised Land (1912)" },
  { name: "Henry Roth", origin: "Austria-Hungary (Galicia)", era: "historic", work: "Call It Sleep (1934)" },
  { name: "Abraham Cahan", origin: "Russian Empire (Lithuania)", era: "historic", work: "The Rise of David Levinsky (1917)" },
  { name: "Bharati Mukherjee", origin: "India", era: "modern", work: "Jasmine (1989)" },
  { name: "Jhumpa Lahiri", origin: "India (UK-born)", era: "modern", work: "Interpreter of Maladies (1999)" },
  { name: "Junot Díaz", origin: "Dominican Republic", era: "modern", work: "The Brief Wondrous Life of Oscar Wao (2007)" },
  { name: "Min Jin Lee", origin: "South Korea", era: "modern", work: "Pachinko (2017)" },
  { name: "Viet Thanh Nguyen", origin: "Vietnam", era: "modern", work: "The Sympathizer (2015)" },
];

const PROVISIONAL_TOPICS = [
  "Arrival ports and processing",
  "Tenement and ethnic enclave life",
  "Language and intergenerational distance",
  "Return-migration ambivalence",
  "Naturalization rituals",
  "Anti-immigrant violence",
  "Second-generation identity",
  "Diaspora politics and homeland",
];

export default function Library() {
  return (
    <div className="view view-library">
      <div className="library-header">
        <h1>Library</h1>
        <div className="library-sub">
          What writers said about arriving
        </div>
      </div>

      <section className="library-section">
        <h3>Seed authors</h3>
        <table className="library-table">
          <thead>
            <tr>
              <th>Author</th>
              <th>Origin</th>
              <th>Era</th>
              <th>Representative work</th>
            </tr>
          </thead>
          <tbody>
            {SEED_AUTHORS.map((a) => (
              <tr key={a.name}>
                <td><em>{a.name}</em></td>
                <td>{a.origin}</td>
                <td>{a.era}</td>
                <td>{a.work}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="library-section">
        <h3>Themes the literature returns to</h3>
        <ul className="topic-cloud">
          {PROVISIONAL_TOPICS.map((t) => (
            <li key={t} className="topic-chip">{t}</li>
          ))}
        </ul>
        <p className="library-note">
          A topic model over the full corpus will produce these themes
          empirically once the texts are loaded. The list above is a
          hand-curated prior — what immigration fiction has historically
          engaged with — and is meant to set expectations, not constrain
          the model.
        </p>
      </section>
    </div>
  );
}
