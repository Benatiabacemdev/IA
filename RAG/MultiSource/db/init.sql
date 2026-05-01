-- Create documents table
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    filepath VARCHAR(1024) NOT NULL,
    modifieddate TIMESTAMP NOT NULL,
    createddate TIMESTAMP NOT NULL,
    size FLOAT NOT NULL,
    uids TEXT
);

-- Create selected_folders table
CREATE TABLE IF NOT EXISTS selected_folders (
    id SERIAL PRIMARY KEY,
    folder_path VARCHAR(1024) NOT NULL UNIQUE,
    source_type VARCHAR(50) NOT NULL DEFAULT 'local',
    selected_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_documents_filename ON documents(filename);
CREATE INDEX IF NOT EXISTS idx_documents_filepath ON documents(filepath);
CREATE INDEX IF NOT EXISTS idx_selected_folders_path ON selected_folders(folder_path);
