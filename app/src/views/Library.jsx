// Library view — literary corpus and topic model.
// Static mockup of the planned BERTopic-driven topic stream; wired in Phase D.

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
          Literary corpus and topic model · Phase D preview
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
        <h3>Provisional topics</h3>
        <ul className="topic-cloud">
          {PROVISIONAL_TOPICS.map((t) => (
            <li key={t} className="topic-chip">{t}</li>
          ))}
        </ul>
        <p className="library-note">
          BERTopic over the assembled corpus will produce these topics
          empirically; the list above is a hand-curated prior of what the
          immigration-fiction literature has historically engaged with.
        </p>
      </section>
    </div>
  );
}
