import streamlit as st

from agent import Agent


def main() -> None:
    st.set_page_config(page_title="Crestline Internal Assistant", page_icon="🤖")
    st.title("Crestline Internal Assistant")
    st.markdown(
        "Ask questions about Crestline internal policies, marketing campaigns, product details, and SQL support."
    )

    query = st.text_input("Your question", "")
    if st.button("Ask") and query.strip():
        with st.spinner("Generating answer..."):
            agent = Agent()
            state = agent.run(query.strip())

        if state.query.error:
            st.error(f"Error: {state.query.error}")
        else:
            st.subheader("Response")
            st.write(state.query.response or "No response returned.")
            st.markdown("---")
            st.write("**Category:**", state.query.category)


if __name__ == "__main__":
    main()
