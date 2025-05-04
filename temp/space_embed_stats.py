from database.page_manager import PageData
from database.space_manager import SpaceInfo
from configuration import sql_file_path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json

# Set up the database engine and session
engine = create_engine(f"sqlite:///{sql_file_path}")
Session = sessionmaker(bind=engine)


def is_embed_nonempty(embed_str):
    try:
        embed = json.loads(embed_str) if embed_str else []
        return bool(embed)
    except Exception:
        return False


def main():
    session = Session()
    # Get all unique spaces from SpaceInfo (preferred) or PageData fallback
    spaces = session.query(SpaceInfo.space_key, SpaceInfo.space_name).all()
    if not spaces:
        # fallback: get from PageData
        spaces = session.query(PageData.space_key).distinct().all()
        spaces = [(s[0], s[0]) for s in spaces]
    print(f"Total spaces: {len(spaces)}\n")
    total_pages = 0
    total_embedded = 0
    for space_key, space_name in spaces:
        pages = session.query(PageData).filter(PageData.space_key == space_key).all()
        with_embeds = [p for p in pages if is_embed_nonempty(p.embed)]
        print(f"Space: {space_key} ({space_name}) | Pages: {len(pages)} | Pages with embeds: {len(with_embeds)}")
        total_pages += len(pages)
        total_embedded += len(with_embeds)
    session.close()
    if total_pages > 0:
        percent = (total_embedded / total_pages) * 100
        print(f"\nOverall: {total_embedded}/{total_pages} pages embedded ({percent:.2f}%)")
    else:
        print("\nNo pages found.")

if __name__ == "__main__":
    main() 